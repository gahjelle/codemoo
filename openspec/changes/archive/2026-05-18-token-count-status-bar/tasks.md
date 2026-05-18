## 1. Dependency

- [x] 1.1 Add `tiktoken` to project dependencies with `uv add tiktoken`

## 2. Token counter module

- [x] 2.1 Create `src/codemoo/core/token_counter.py` with module-level `cl100k_base` encoder instance
- [x] 2.2 Implement `estimate_tokens(messages: list[Message]) -> int` summing tokens from `content` and `tool_calls_json` per message, treating `None` as empty string
- [x] 2.3 Write `tests/core/test_token_counter.py` covering: empty list, content-only, tool_calls_json, None fields

## 3. ContextStatus widget

- [x] 3.1 Update `ContextStatus` to store and display both message count and token count
- [x] 3.2 Update the update method signature to accept token count alongside message count
- [x] 3.3 Implement display formatting: `"N messages · ~Xk tokens"` (≥ 1000) or `"N messages · ~X tokens"` (< 1000), always with `~` prefix

## 4. ChatApp integration

- [x] 4.1 Import `estimate_tokens` and `build_context` at the `ChatApp` call site
- [x] 4.2 Update `ChatApp._dispatch` to compute `estimate_tokens(build_context(self._chat_context))` and pass it to `ContextStatus`

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 5.2 Run `uv run ty check src/ tests/`
- [x] 5.3 Run `uv run pytest`
- [ ] 5.4 Start `uv run codemoo` with a bot that has `context_management` capability, send a few messages, and confirm the status bar shows both message count and token estimate

## 6. Documentation

- [x] 6.1 Review `AGENTS.md` and update the `context_management` capability description to mention token count display
