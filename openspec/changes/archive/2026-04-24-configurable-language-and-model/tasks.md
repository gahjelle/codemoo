## 1. Config Helper

- [x] 1.1 Create `src/codemoo/config.py` with `language_instruction() -> str` that reads `CODEMOO_LANGUAGE` and returns `" Answer in <value>."` or `""`
- [x] 1.2 Add unit tests for `language_instruction()` in `tests/test_config.py` covering set, unset, and empty-string cases

## 2. LLM Backend

- [x] 2.1 Update `create_mistral_backend()` in `src/codemoo/llm/backend.py` to read `CODEMOO_MISTRAL_MODEL` as the default for the `model` parameter (falling back to `"mistral-small-latest"`)
- [x] 2.2 Update `tests/llm/test_backend.py` to add scenarios for `CODEMOO_MISTRAL_MODEL` set and unset

## 3. CommentatorBot

- [x] 3.1 Remove all hardcoded `"Answer in Norwegian."` clauses from persona prompts in `src/codemoo/core/bots/commentator_bot.py`
- [x] 3.2 Append `language_instruction()` to each persona's system prompt string

## 4. ErrorBot

- [x] 4.1 In `ErrorBot.format_error()` in `src/codemoo/core/bots/error_bot.py`, append `language_instruction()` to the system message content before passing it to the backend

## 5. Demo Slides

- [x] 5.1 In `_build_llm_prompt()` in `src/codemoo/chat/slides.py`, append `language_instruction()` to the returned prompt string

## 6. Verification

- [x] 6.1 Run `uv run pytest` — all tests pass
- [x] 6.2 Run `uv run ruff check .` and `uv run ruff format .` — no lint or format errors
- [x] 6.3 Run `uv run ty check .` — no type errors
