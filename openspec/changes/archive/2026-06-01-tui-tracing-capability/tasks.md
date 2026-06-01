## 1. Core Data Model

- [x] 1.1 Create `src/codemoo/core/trace_store.py` with `TraceEntry` (dataclass, fields: `url: str`, `request: dict[str, object]`, `response: dict[str, object] | None = None`) and `TraceStore` (dataclass, fields: `entries: list[TraceEntry]` defaulting to empty list, methods: `make_tracer() -> Tracer`, `clear() -> None`)
- [x] 1.2 Implement `TraceStore.make_tracer()`: `on_request` appends a new `TraceEntry`; `on_response` replaces the last entry's response via `dataclasses.replace` (no-op if entries is empty)
- [x] 1.3 Write unit tests in `tests/core/test_trace_store.py` covering: empty store construction, `on_request` appends entry, `on_response` fills response, `on_response` with empty store is no-op, `clear` empties entries

## 2. Schema Update

- [x] 2.1 In `src/codemoo/config/schema.py`, extend `BotCapability` Literal to include `"tracing"` alongside `"context_management"`

## 3. TUI Setup Wiring

- [x] 3.1 In `src/codemoo/frontends/tui.py`, add `trace_store: TraceStore` field to `SetupResult`
- [x] 3.2 In `_setup()`: create `TraceStore()`, call `store.make_tracer()`, pass `tracer=tracer` to `resolve_backend`, include `trace_store=store` in the returned `SetupResult`
- [x] 3.3 Repeat the same wiring in `_setup_for_launcher()` and `select()`

## 4. ChatApp Integration

- [x] 4.1 In `src/codemoo/chat/app.py`, add `trace_store: TraceStore` parameter to `ChatApp.__init__` and store as `self._trace_store`
- [x] 4.2 Add `_bind_tracing` function (no-op body) and register it in `_CAPABILITY_BINDERS["tracing"]`
- [x] 4.3 In `ChatApp.on_key`, add Ctrl-T handling before the demo-mode guard: if `"tracing" in self._active_capabilities`, push `TraceModal(self._trace_store)` and return
- [x] 4.4 In the message dispatch path, call `self._trace_store.clear()` before the first LLM call of each turn

## 5. TraceModal

- [x] 5.1 Create `src/codemoo/chat/trace_modal.py` with `TraceModal(ModalScreen)` accepting a `TraceStore`; dismiss on any key press
- [x] 5.2 Implement the rendering loop: for each `TraceEntry`, render TOOL RESULT (conditional), REQUEST (always), RESPONSE (always), TOOL CALL (conditional) sections with `json.dumps(data, indent=2)`
- [x] 5.3 Implement Anthropic tool result extraction from request: last message where `content` is a list and `content[0]["type"] == "tool_result"` → display content
- [x] 5.4 Implement OpenAI tool result extraction from request: last message where `role == "tool"` → display content
- [x] 5.5 Implement Anthropic tool call extraction from response: find item in `response["content"]` with `"type": "tool_use"` → format as `name(key=repr(val), ...)`
- [x] 5.6 Implement OpenAI tool call extraction from response: `response["choices"][0]["message"]["tool_calls"][0]["function"]` → parse `.arguments` with `json.loads`, format as `name(key=repr(val), ...)`
- [x] 5.7 Place structural CSS (height, layout, scroll) in `TraceModal.DEFAULT_CSS`; add visual CSS (colors, borders, padding) to `src/codemoo/chat/chat.tcss`

## 6. Config Update

- [x] 6.1 In `src/codemoo/config/codemoo.toml`, update `[bots.CompactBot.variants.codemoo]` to set `capabilities = ["context_management", "tracing"]`

## 7. Documentation Review

- [x] 7.1 Read `AGENTS.md` and update the capabilities table to include `tracing` with its UI effect description
- [x] 7.2 Read `README.md` and update if any end-user-visible feature documentation needs to mention the Ctrl-T trace overlay

## 8. Verification

- [x] 8.1 Run `uv run ruff format src/ tests/`
- [x] 8.2 Run `uv run ruff check src/ tests/`
- [x] 8.3 Run `uv run ty check src/ tests/`
- [x] 8.4 Run `uv run pytest` and confirm all tests pass
- [x] 8.5 Launch `uv run codemoo --bot CompactBot --variant codemoo`, send a message, press Ctrl-T, and verify the trace modal shows the LLM request and response payloads
