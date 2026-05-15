## 1. Protocol and dispatch

- [x] 1.1 Update `ChatParticipant.on_message` in `src/codemoo/core/participant.py`: remove `message: ChatMessage` parameter, add docstring noting the `context[-1]` precondition
- [x] 1.2 Update `HumanParticipant.on_message` in `src/codemoo/core/participant.py`: remove `message` parameter and its `# noqa: ARG002`; keep `context` parameter with `# noqa: ARG002`
- [x] 1.3 Update the call site in `src/codemoo/chat/app.py` (`_collect_replies`): `participant.on_message(message, self._chat_context)` → `participant.on_message(self._chat_context)`; add a comment documenting the invariant that `self._chat_context[-1]` is the triggering message

## 2. Bots — remove message parameter

- [x] 2.1 `echo_bot.py`: remove `message` parameter; change `message.text` → `context[-1].content.text`; drop `ChatMessage` import
- [x] 2.2 `llm_bot.py`: remove `message` parameter; change `message.text` → `context[-1].content.text`; drop `ChatMessage` import
- [x] 2.3 `chat_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.4 `system_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.5 `single_turn_tool_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.6 `agent_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.7 `guard_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.8 `project_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.9 `memory_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import
- [x] 2.10 `retry_bot.py`: remove `message` parameter and `# noqa: ARG002`; drop `ChatMessage` import

## 3. Tests

- [x] 3.1 Add `user_ctx(text: str) -> list[ContextItem]` helper in a shared conftest or at the top of each bot test file — returns `[ContextItem(content=UserMessageContent(text), turn_id=0)]`
- [x] 3.2 Update `tests/core/bots/test_echo_bot.py`: replace `on_message(msg, [])` with `on_message(user_ctx(msg.text))`; remove `ChatMessage` fixture and import
- [x] 3.3 Update `tests/core/bots/test_llm_bot.py`: replace `on_message(msg, [])` with `on_message(user_ctx(msg.text))`; remove `ChatMessage` helper and import
- [x] 3.4 Update `tests/core/bots/test_system_bot.py`: replace all `on_message(msg, ctx)` call sites — supply `user_ctx(text)` as the base and extend with any existing context items; remove `ChatMessage` helper and import
- [x] 3.5 Update `tests/core/bots/test_tool_bot.py`: replace all `on_message(msg, [])` call sites with `on_message(user_ctx(...))`; remove `ChatMessage` helper and import
- [x] 3.6 Update `tests/core/test_participant.py`: update the protocol conformance test's `on_message` signature; remove `ChatMessage` import

## 4. Verification

- [x] 4.1 Run `uv run ruff format src/ tests/`
- [x] 4.2 Run `uv run ruff check src/ tests/`
- [x] 4.3 Run `uv run ty check src/ tests/`
- [x] 4.4 Run `uv run pytest`

## 5. Documentation

- [x] 5.1 Review `AGENTS.md` and update the Context Architecture section if it references the `on_message` signature
