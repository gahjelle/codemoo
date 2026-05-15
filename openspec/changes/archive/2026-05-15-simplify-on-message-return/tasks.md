## 1. Protocol and HumanParticipant

- [x] 1.1 Update `ChatParticipant.on_message` return type to `list[ContextItem]` in `src/codemoo/core/participant.py`
- [x] 1.2 Update `HumanParticipant.on_message` to return `[]` (remove tuple)

## 2. Simple bots (single ContextItem return)

- [x] 2.1 Update `EchoBot.on_message` in `src/codemoo/core/bots/echo_bot.py` — drop `ChatMessage`, return `[new_item]`
- [x] 2.2 Update `LlmBot.on_message` in `src/codemoo/core/bots/llm_bot.py` — drop `ChatMessage`, return `[new_item]`
- [x] 2.3 Update `ChatBot.on_message` in `src/codemoo/core/bots/chat_bot.py` — drop `ChatMessage`, return `[new_item]`
- [x] 2.4 Update `SystemBot.on_message` in `src/codemoo/core/bots/system_bot.py` — drop `ChatMessage`, return `[new_item]`
- [x] 2.5 Update `ErrorBot.on_message` in `src/codemoo/core/bots/error_bot.py` — drop tuple, return `[]`

## 3. Tool bots (multi-item return, list construction)

- [x] 3.1 Update `SingleTurnToolBot.on_message` in `src/codemoo/core/bots/single_turn_tool_bot.py` — drop `ChatMessage`, return list directly (no mutation)
- [x] 3.2 Update `AgentBot.on_message` in `src/codemoo/core/bots/agent_bot.py` — drop `ChatMessage`, replace comprehension+append with `[*[...], last_item]`
- [x] 3.3 Update `GuardBot.on_message` in `src/codemoo/core/bots/guard_bot.py` — drop `ChatMessage`, replace comprehension+append with `[*[...], last_item]`
- [x] 3.4 Update `ProjectBot.on_message` in `src/codemoo/core/bots/project_bot.py` — drop `ChatMessage`, replace comprehension+append with `[*[...], last_item]`
- [x] 3.5 Update `MemoryBot.on_message` in `src/codemoo/core/bots/memory_bot.py` — drop `ChatMessage`, replace comprehension+append with `[*[...], last_item]`

## 4. RetryBot

- [x] 4.1 Change `RetryBot._escalation_message` in `src/codemoo/core/bots/retry_bot.py` to return `str` instead of `ChatMessage`
- [x] 4.2 Update `RetryBot.on_message` — drop `ChatMessage`, replace comprehension+append with `[*[...], last_item]`, use string from `_escalation_message` directly

## 5. App

- [x] 5.1 Update `_collect_replies` in `src/codemoo/chat/app.py` — unpack only `new_items`, derive `ChatMessage` from last item when `AssistantMessageContent`, attach `thinking_time` after derivation, update `finally` guard to check derived `reply is None`

## 6. Tests

- [x] 6.1 Update `tests/core/test_participant.py` — change unpacking from `(reply, _)` to `new_items = ...`
- [x] 6.2 Update `tests/core/bots/test_echo_bot.py`
- [x] 6.3 Update `tests/core/bots/test_llm_bot.py`
- [x] 6.4 Update `tests/core/bots/test_chat_bot.py`
- [x] 6.5 Update `tests/core/bots/test_system_bot.py`
- [x] 6.6 Update `tests/core/bots/test_error_bot.py`
- [x] 6.7 Update `tests/core/bots/test_tool_bot.py`
- [x] 6.8 Update `tests/core/bots/test_read_bot.py`
- [x] 6.9 Update `tests/core/bots/test_change_bot.py`
- [x] 6.10 Update `tests/core/bots/test_agent_bot.py`
- [x] 6.11 Update `tests/core/bots/test_guard_bot.py`
- [x] 6.12 Update `tests/chat/test_collect_replies.py`

## 7. Verification

- [x] 7.1 `uv run ruff format src/ tests/`
- [x] 7.2 `uv run ruff check src/ tests/`
- [x] 7.3 `uv run ty check src/`
- [x] 7.4 `uv run pytest`

## 8. Documentation

- [x] 8.1 Read `PLANS.md` and update if the return-type contract is documented there
- [x] 8.2 Read `AGENTS.md` and update the bot protocol description under Context Architecture if necessary
