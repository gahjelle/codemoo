## 1. AgentBot Core

- [x] 1.1 Create `src/codemoo/core/bots/agent_bot.py` with `AgentBot` dataclass — fields mirror `GeneralToolBot` (`name`, `emoji`, `backend`, `human_name`, `tools`, `instructions`, `max_messages`); `is_human = False`
- [x] 1.2 Implement `on_message`: build context, loop `complete_step` until `TextResponse`, accumulate `ToolUse` + `tool`-role messages in a local list each iteration, return `ChatMessage` with final text
- [x] 1.3 Export `AgentBot` from `src/codemoo/core/bots/__init__.py`

## 2. Tests

- [x] 2.1 Write `tests/core/bots/test_agent_bot.py` — test immediate `TextResponse` (no tool call), single tool call then text, and two sequential tool calls then text
- [x] 2.2 Verify `is_human` is `False` and `reply.sender == bot.name`

## 3. Registration

- [x] 3.1 Add `AgentBot` instance (name `"Loom"`, emoji `♾️`, tools `[run_shell, read_file, reverse_string]`) to `available_bots` list in `src/codemoo/__init__.py`, after `ShellBot`

## 4. Validation

- [x] 4.1 Run `uv run pytest` — all tests pass
- [x] 4.2 Run `uv run ruff check . && uv run ruff format --check .` — no lint or format errors
- [x] 4.3 Run `uv run ty check` — no type errors
