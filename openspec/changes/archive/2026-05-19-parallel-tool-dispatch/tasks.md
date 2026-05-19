## 1. Backend Protocol

- [x] 1.1 Change `complete()` overload signatures in `LLMBackend` protocol (`backend.py`): `str | ToolUse` → `str | list[ToolUse]`
- [x] 1.2 Add `merge_tool_uses(uses: list[ToolUse]) -> Message` pure function to `backend.py`

## 2. Anthropic Backend

- [x] 2.1 Update `_AnthropicBackend.complete()` to collect all `tool_use` blocks from `response.content` and return `list[ToolUse]` (each with its own single-call `assistant_message`)
- [x] 2.2 Fix `_serialize()` in `anthropic.py`: merge consecutive `role="tool"` messages into a single `{"role": "user", "content": [tool_result, ...]}` batched user message

## 3. OpenAI-Like Backend

- [x] 3.1 Update `OpenAILikeBackend.complete()` to collect all entries from `message.tool_calls` and return `list[ToolUse]`

## 4. SingleTurnToolBot

- [x] 4.1 Update `SingleTurnToolBot.on_message()`: `isinstance(response, ToolUse)` → `isinstance(response, list)`; use `response[0]` for the single call

## 5. AgentBot and Downstream Bots

- [x] 5.1 Update `AgentBot.on_message()`: check `isinstance(response, list)`, loop over all uses with `for`-loop, call `merge_tool_uses()` for combined assistant message, append all tool-result messages before next `complete()` call
- [x] 5.2 Update `GuardBot.on_message()` identically to AgentBot; approval check remains per-call inside the loop
- [x] 5.3 Update `MemoryBot.on_message()` identically to GuardBot
- [x] 5.4 Update `ProjectBot.on_message()` identically to GuardBot
- [x] 5.5 Update `RetryBot.on_message()` identically to GuardBot
- [x] 5.6 Update `CompactBot` tool-call handling identically to GuardBot

## 6. CLI Frontend

- [x] 6.1 Update `tool()` in `cli.py`: `isinstance(step, ToolUse)` → `isinstance(step, list)`; use `step[0]` for the single call
- [x] 6.2 Update `agent()` in `cli.py`: `isinstance(response, ToolUse)` → `isinstance(response, list)`; loop over all uses with `for`-loop, use `merge_tool_uses()` for combined assistant message, append all tool-result messages before next `complete()` call

## 7. Tests

- [x] 7.1 Update all backend tests that mock `complete()` returning `ToolUse(...)` → `[ToolUse(...)]`
- [x] 7.2 Update all bot tests that mock `complete()` returning `ToolUse(...)` → `[ToolUse(...)]`
- [x] 7.3 Add test for `merge_tool_uses()`: single use, multiple uses
- [x] 7.4 Add test for Anthropic `_serialize()` merging consecutive tool messages
- [x] 7.5 Add test for `AgentBot` dispatching two tool calls from one `complete()` response (verifies no extra LLM round-trip)

## 8. Verification

- [x] 8.1 `uv run ruff format src/ tests/`
- [x] 8.2 `uv run ruff check src/ tests/`
- [x] 8.3 `uv run ty check src/ tests/`
- [x] 8.4 `uv run pytest`

## 9. Documentation

- [x] 9.1 Read `AGENTS.md`, `PLANS.md`, `README.md` and update any references to `complete()` return type or the AgentBot tool-dispatch loop
