## Context

The TUI already has a `Tracer` dataclass (in `core/tracer.py`) that lets backends emit request/response payloads via callbacks. The `demoo` CLI uses it via `RichTracer` to print full traces to the terminal. In the TUI, a `Tracer` is threaded through `resolve_backend` but its callbacks are always `None` — nothing accumulates the data.

Adding a `tracing` BotCapability means: (1) accumulate the payloads across a turn, (2) expose them in a Ctrl-T modal, without changing bots, dispatch infrastructure, or the backend contract.

## Goals / Non-Goals

**Goals:**
- Accumulate per-turn LLM traffic in a `TraceStore` wired via the existing `Tracer` hook
- Display the last turn's traffic in a scrollable Textual modal on Ctrl-T
- Extract tool call and tool result sections from raw payloads (both Anthropic and OpenAI wire formats)
- Gate the feature behind `capabilities = ["tracing"]` using the existing `_CAPABILITY_BINDERS` pattern

**Non-Goals:**
- No changes to `dispatch_tool`, bot dataclasses, or `CommentatorBot`
- No persistent trace log across turns
- No horizontal scrolling or line-wrapping in the modal
- No trace in non-TUI runners (`demoo`, CLI)

## Decisions

### TraceStore accumulates entries; Tracer callbacks are closures over it

The `Tracer` dataclass already has `on_request` and `on_response` optional callbacks. Rather than subclassing or extending `Tracer`, we introduce `TraceStore` in `core/trace_store.py` with a `make_tracer()` factory that returns a `Tracer` whose callbacks close over the store's `entries` list.

**Alternative considered**: modify `Tracer` itself to carry state. Rejected — `Tracer` is intentionally a thin data carrier; accumulation logic in `core/` would pull TUI concerns into a shared module.

### TraceStore lives in `core/`, TraceModal in `chat/`

`TraceStore` has no Textual dependency and can be unit-tested in isolation. `TraceModal` is a Textual `ModalScreen` and belongs alongside `ApprovalModal` in `chat/`.

### Store is cleared at the start of each dispatch, not at the end

Clearing at start (before the first LLM call of the turn) means Ctrl-T during a running turn shows the previous turn's data, not a partial view. Clearing at end would show nothing if the user opens the modal between turns.

### Tool call/result extraction parses payloads directly

There are exactly two wire formats in the codebase: Anthropic (top-level `"content"` list) and OpenAI-like (top-level `"choices"`). All non-Anthropic backends extend `OpenAILikeBackend`. Detection is a simple key check; extraction is a few dict lookups.

**Alternative considered**: add a `tool_events` hook to `dispatch_tool`. Rejected — it would require touching every bot and adding a new protocol just to surface data already present in the payloads.

### Ctrl-T is handled before the demo-mode guard

`ChatApp.on_key` has a guard that short-circuits non-demo keys when `_demo_context is None`. Ctrl-T must work in both demo and normal mode, so it is checked first:

```python
if event.key == "ctrl+t" and "tracing" in self._active_capabilities:
    self._open_trace_modal()
    return
```

### `_bind_tracing` is a no-op function

Unlike `context_management`, which mounts a visible status bar widget, `tracing` requires no persistent widget — the modal is opened on demand. The binder exists so the dispatch table is consistent and future additions (e.g. a keyboard hint in the status bar) have a natural home.

### Modal layout: VerticalScroll only, no truncation

Long JSON payloads overflow off-screen to the right. A horizontal scrollbar adds complexity for a developer-facing debug view; users can resize the terminal if needed.

## Risks / Trade-offs

- **Large payloads**: A turn with many tool calls or long file contents can produce very large JSON blobs in the modal. Mitigation: the modal already uses `VerticalScroll`; users can close it at any time. No truncation is intentional — partial payloads are worse than slow scrolling for debugging.
- **Two wire formats**: If a new backend uses a third format, tool call extraction silently shows nothing. Mitigation: the extraction is isolated in `TraceModal`; adding a new format requires touching only that file.
- **Entry pairing**: `on_response` matches the response to the last entry. If a backend fires `on_response` without a preceding `on_request`, the call is silently ignored. This is consistent with the existing `Tracer` contract.

## Open Questions

None — all decisions are captured above.
