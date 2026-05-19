## Context

`ChatApp` owns `self._chat_context: list[ContextItem]` — the authoritative intermediate layer between the chat log and LLM wire format. The existing `context_display` capability (formerly `context_management`) already mounts a `ContextStatus` widget that shows item count and estimated token usage. The capability system uses `_CAPABILITY_BINDERS` to wire up UI widgets on mount, and `on_key` for keyboard handling. `ApprovalModal` is the established pattern for dismissible read-only overlays.

## Goals / Non-Goals

**Goals:**
- Rename the capability string without changing any runtime behavior
- Make Ctrl-R available outside demo mode (clear context, re-run startup)
- Add a read-only context inspector modal accessible via Ctrl-X

**Non-Goals:**
- No live updates in the modal while it's open
- No context editing (selecting, disabling, summarising items) — that's a future capability
- No visual shortcut hints outside demo mode

## Decisions

### Capability rename is a string constant change only
The rename from `"context_management"` to `"context_display"` touches the BotCapability Literal in `schema.py`, the `_CAPABILITY_BINDERS` key in `app.py`, and 8 `capabilities` entries in `codemoo.toml`. No logic or behavior changes at all — just the string.

### Ctrl-X over Ctrl-C for the modal shortcut
Ctrl-C is a system binding in Textual, mapped to `action_help_quit` ("copy" when a textarea is focused, "suggest quit" otherwise). Repurposing it would create confusing layered behavior. Ctrl-X has no conflicts in terminals, Textual's defaults, or the existing shortcut map, and has a reasonable mnemonic ("eXamine context").

### Snapshot data model — no live updates
`ChatApp` passes a snapshot of `self._chat_context` and the pre-calculated token count (already computed by `_dispatch` for `ContextStatus`) when pushing the modal. The modal stores these in `__init__` and renders them statically. Alternative (live binding via reactive) adds complexity and is unnecessary for a read-only inspector.

### ModalScreen as the overlay pattern
`ModalScreen` is already used for `ApprovalModal` and `SlideScreen`. It provides focus trapping, Escape dismissal, and dim background automatically. A custom Screen would require reimplementing all of that.

### One-liner format with fixed columns
Each row uses `{glyph}  {type:<4}  {preview}` with the mode glyph and 4-char type tag as fixed columns before the free-text preview. This makes mode and type scannable without needing color coding. Pin state sits between glyph and type: `{glyph} 📌 {type:<4}  {preview}` vs `{glyph}    {type:<4}  {preview}`. The 📌 emoji is double-width, so the alignment shifts slightly for pinned items — acceptable since pinned items are rare.

### Turn separators as dim Labels
A thin dim `Label` containing `──` (or similar) is inserted between groups of items whose `turn_id` changes. A Textual `Rule` widget would also work but a styled `Label` is lighter and consistent with the existing `restart-divider` pattern.

### Token count reuse — no recalculation
`_dispatch` already calls `estimate_tokens(build_context(self._chat_context))` after each bot turn to update `ContextStatus`. `ChatApp` passes this pre-calculated count to `ContextInspectModal` at open time. Recalculating inside the modal would be redundant and potentially stale-in-the-other-direction (modal opens mid-dispatch).

### Ctrl-R gating — capability vs always-on
Ctrl-R is made always-on (no capability gate) since restarting a conversation is a universally useful action regardless of which bot is loaded. The modal (Ctrl-X) is gated by `"context_display" in self._active_capabilities` because it's only meaningful when that capability is active and `ContextStatus` is mounted.

## Risks / Trade-offs

- [📌 double-width emoji shifts alignment] → Accepted; pinned items are rare and the shift is minor
- [Modal content stale if opened during a bot turn] → Accepted; snapshot-at-open is simple and the race window is narrow
- [Lines truncate silently at 90% width] → Accepted for now; ToolUseContent with long args may lose output preview. Future work: explicit truncation with `…`

## Open Questions

_(none — all design decisions resolved during exploration)_
