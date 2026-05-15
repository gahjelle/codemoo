## Context

Codemoo bots currently build `list[Message]` from `list[ChatMessage]` inline inside each `on_message()` call. Tool call traces are ephemeral — they exist only within the current turn's local variables and are never persisted. The `ChatParticipant` protocol passes `history: list[ChatMessage]`, which contains only final text replies, not the tool calls that produced them. There is no mechanism to filter, compress, edit, inject, or reorder context items.

This change introduces `list[ContextItem]` as an explicit, owned, shapeable intermediate layer sitting between the chat log and the LLM wire format.

## Goals / Non-Goals

**Goals:**
- Define `ContextItem` and `ContextContent` as immutable value types
- Define a `build_context()` pure function that converts `list[ContextItem]` to `list[Message]`
- Update the `ChatParticipant` protocol: `on_message` receives and returns `list[ContextItem]`
- Transfer context ownership to `ChatApp`
- Update all bots to the new protocol

**Non-Goals:**
- UI modal for interactive context manipulation
- LLM-powered summary generation
- Budget-aware context window trimming
- Context persistence across sessions
- Changes to LLM backend wire formats or provider adapters

## Decisions

### ContextContent as a discriminated union

**Decision:** Seven concrete content types (`UserMessageContent`, `AssistantMessageContent`, `ToolUseContent`, `InjectedContent`, `SystemContent`) form a closed union.

**Rationale:** A closed union makes `build_context()` exhaustive and type-safe. Adding a new content type is a deliberate, auditable change. A single flexible dict or string-typed payload would lose type safety and make the context builder's branching implicit.

**Alternative considered:** A single `Content` dataclass with optional fields. Rejected — it makes illegal states representable (e.g. a tool result with no call_id) and removes the compiler's help.

---

### ToolUseContent wraps call and result as an atomic pair

**Decision:** Tool call and tool result are stored together in a single `ToolUseContent` rather than as two separate `ContextItem`s.

**Rationale:** The LLM API requires every tool result to be preceded by its corresponding tool call. Keeping them as a pair makes this invariant structural rather than relational — no orphan detection is needed in `build_context()`. The context builder unrolls a single `ToolUseContent` into two `Message`s.

**Alternative considered:** Separate `ToolCallContent` and `ToolResultContent` items linked by `call_id`. Rejected — it requires the context builder to detect and skip orphaned results, and makes it possible for the UI to accidentally violate the pairing invariant.

**Consequence:** `ContextItem`s for a turn are created after the turn's agentic loop completes, not during it. The bot's internal loop continues to use a local `list[Message]` (unchanged from today), and produces `list[ContextItem]` when returning from `on_message()`.

---

### ChatApp owns the authoritative list[ContextItem]; bots return only new items

**Decision:** `ChatApp._context: list[ContextItem]` is the single source of truth. Bots receive the full context as read-only input but return only the new items they produced this turn. The App merges: `self._context = [*self._context, *new_items]`. Modifications to existing items (set_mode, set_summary, inject_at, etc.) are exclusively a user operation via the planned UI modal — no bot may alter the authoritative history.

**Rationale:** This gives bots read access to full context for LLM input construction while making the separation of concerns structural: bots append, users shape. A bot cannot accidentally corrupt history even if it tried. It also simplifies bot implementations — they only produce, never transform.

**Alternative considered:** Bot returns the full updated list. Rejected — it requires every bot to thread the entire list correctly and opens the door for bots to modify existing items, blurring the authority boundary between bot and user.

---

### Immutable list with pure operations

**Decision:** `list[ContextItem]` is treated as an immutable value. All context operations (add, replace, set_mode, inject) are pure functions returning new lists. `ContextItem` itself is a frozen dataclass.

**Rationale:** Eliminates aliasing bugs. Makes operations trivially testable. Enables free undo by keeping the previous list reference.

---

### mode enum: ORIGINAL / EDITED / SUMMARY / DISABLED

**Decision:** A single `mode` field on `ContextItem` controls which content layer is active. Three content layers exist: `content` (immutable original), `edited` (user rewrite), `summary` (compression). Mode selects among them; `content` is never modified.

**Rationale:** Supports the full non-destructive editing lifecycle — disable and re-enable, summarize and restore, edit and then summarize the edit — without losing any prior state. Each mode transition is reversible.

**Invariants:** `mode == EDITED → edited is not None`; `mode == SUMMARY → summary is not None`.

---

### turn_id as a monotonically increasing int

**Decision:** `turn_id = max(item.turn_id for item in context) + 1` if context is non-empty, else `0`. All items produced in one `on_message()` call share the same `turn_id`.

**Rationale:** Integer turn IDs are human-readable in the UI and can be computed locally by any bot without coordination. The monotonic convention is simple and deterministic.

---

### Uniform protocol for all bots

**Decision:** All bots — including `EchoBot` and `LlmBot` — follow the new `on_message(message, context) -> tuple[ChatMessage | None, list[ContextItem]]` signature. Simple bots ignore the incoming context but still return the updated list.

**Rationale:** A uniform protocol means `ChatApp` does not need to branch on bot type. Simple bots append their reply as an `AssistantMessageContent` item and return; smart bots use `build_context()` to construct LLM input and produce richer context items.

## Risks / Trade-offs

- **All bot signatures break.** → Acceptable; we control all bots and there are no external callers. A single migration pass covers all of them.
- **Test updates required.** Any test asserting on `history` parameter or return type must be updated. → Straightforward mechanical change; tests should be clearer after (context is richer than history).
- **ContextItems born after the turn.** Bots cannot inspect the evolving intra-turn context during an agentic loop. → This is intentional; the loop is internal. If intra-turn context visibility is ever needed it can be added later without changing the protocol.

## Migration Plan

1. Define `ContextItem`, `ContextContent` types, `ItemMode` enum, and pure list operations in `codemoo/core/context.py`.
2. Define `build_context()` in `codemoo/core/context_builder.py`.
3. Update `ChatParticipant` protocol in `codemoo/core/participant.py`.
4. Update `ChatApp` to own `_context` and pass/receive it on each dispatch.
5. Update all bots in dependency order: `EchoBot` → `LlmBot` → `ChatBot` → `SystemBot` → `SingleTurnToolBot` (and subclasses) → `AgentBot` → remaining bots.
6. Update tests.

No rollback strategy required — this is internal tooling with no external API surface.

## Open Questions

None. All key decisions were resolved during the exploration phase.
