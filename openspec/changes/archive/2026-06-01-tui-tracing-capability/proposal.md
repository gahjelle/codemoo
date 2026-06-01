## Why

The TUI has no way to inspect what the LLM is actually receiving and sending during a turn. Adding a `tracing` capability and a Ctrl-T overlay gives developers and demo audiences a live view of request/response payloads without wiring new hooks into bots or dispatch infrastructure.

## What Changes

- New `"tracing"` value added to the `BotCapability` Literal in `schema.py`
- New `TraceStore` / `TraceEntry` data model in `core/trace_store.py` that accumulates `(url, request, response)` triples via a `Tracer`
- New `TraceModal` Textual `ModalScreen` in `chat/trace_modal.py` — opened by Ctrl-T, shows the last turn's LLM traffic with tool call / tool result extraction
- `SetupResult` gains a `trace_store` field; all three TUI setup paths create and thread a `TraceStore` through to `ChatApp`
- `ChatApp` clears the store at the start of each dispatch, accepts Ctrl-T in `on_key`, and registers a `_bind_tracing` binder in `_CAPABILITY_BINDERS`
- CompactBot `codemoo` variant is the first to declare `capabilities = ["context_management", "tracing"]`

## Non-goals

- No changes to `dispatch_tool`, bot dataclasses, or `CommentatorBot`
- No persistent trace log across turns — the store is always cleared at the start of each new user message
- No line-wrapping or horizontal scrolling in the modal — long JSON lines overflow off-screen

## Capabilities

### New Capabilities

- `tui-trace-store`: `TraceStore` and `TraceEntry` dataclasses that accumulate LLM request/response payloads via a `Tracer`; provides `make_tracer()` and `clear()`
- `tui-trace-modal`: `TraceModal(ModalScreen)` Textual overlay opened by Ctrl-T; renders each trace entry as TOOL RESULT / REQUEST / RESPONSE / TOOL CALL sections with pretty-printed JSON

### Modified Capabilities

- `bot-capability-declarations`: Add `"tracing"` to the `BotCapability` Literal and register a `_bind_tracing` entry in `_CAPABILITY_BINDERS`

## Impact

- `src/codemoo/config/schema.py` — BotCapability extended
- `src/codemoo/core/trace_store.py` — new file
- `src/codemoo/chat/trace_modal.py` — new file
- `src/codemoo/frontends/tui.py` — SetupResult and all three setup paths updated
- `src/codemoo/chat/app.py` — trace_store param, Ctrl-T handler, binder, dispatch clear
- `src/codemoo/config/codemoo.toml` — CompactBot codemoo variant updated
