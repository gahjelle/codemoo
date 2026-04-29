## 1. Inline context in simple bots

- [x] 1.1 Update `ChatBot`: remove `human_name` and `max_messages` fields, remove `build_llm_context` import, add `Message` import, inline context construction
- [x] 1.2 Update `SystemBot`: remove `human_name` and `max_messages` fields, remove `build_llm_context` import, inline context construction with system message first

## 2. Inline context in tool-loop bots

- [x] 2.1 Update `AgentBot`: remove `human_name` and `max_messages` fields, remove `build_llm_context` import, inline initial context construction
- [x] 2.2 Update `GuardBot`: same as AgentBot
- [x] 2.3 Update `SingleTurnToolBot`: remove `human_name` and `max_messages` fields, remove `build_llm_context` import, inline context construction assigned to `messages` (reused for `follow_up`)

## 3. Remove build_llm_context

- [x] 3.1 Delete `build_llm_context` from `src/codemoo/core/backend.py`

## 4. Update factory and frontend

- [x] 4.1 Remove `human_name` parameter from `_make_bot` and `make_bots` in `src/codemoo/core/bots/__init__.py`; remove `human_name=human_name` from all bot constructor calls inside `_make_bot`
- [x] 4.2 Remove `human_name=human.name` from both `make_bots` calls in `src/codemoo/frontends/tui.py`

## 5. Update tests

- [x] 5.1 Delete `tests/core/test_backend.py` (tested `build_llm_context` which is now removed)
- [x] 5.2 Update `tests/core/bots/test_chat_bot.py`: remove `human_name` from fixture and constructor calls; update the "filters other bots" test to assert third-party messages now appear as `role="user"`; delete clipping tests
- [x] 5.3 Update `tests/core/bots/test_system_bot.py`: same changes as chat_bot tests
- [x] 5.4 Update `tests/core/bots/test_agent_bot.py`: remove `human_name` from bot constructors
- [x] 5.5 Update `tests/core/bots/test_guard_bot.py`: remove `human_name` from bot constructors
- [x] 5.6 Update `tests/core/bots/test_make_bots.py`: remove `human_name="You"` from `make_bots` calls

## 6. Verify

- [x] 6.1 Run `uv run ruff format src/ tests/`
- [x] 6.2 Run `uv run ruff check src/ tests/`
- [x] 6.3 Run `uv run ty check src/ tests/`
- [x] 6.4 Run `uv run pytest`

## 7. Documentation review

- [x] 7.1 Review `AGENTS.md`, `PLANS.md`, and any bot-facing docs; update if `human_name`, `max_messages`, or `build_llm_context` are mentioned
