## 1. Core backend module

- [x] 1.1 Create `src/codemoo/core/backend.py` with `Role` type alias, `Message` frozen dataclass, and `LLMBackend` protocol
- [x] 1.2 Implement `build_llm_context(history, current, bot_name, human_name, max_messages) -> list[Message]` in `core/backend.py`
- [x] 1.3 Add `tests/core/test_backend.py` with synchronous tests for `build_llm_context` (filtering, role mapping, clipping, current-message appending)

## 2. Core bots package

- [x] 2.1 Create `src/codemoo/core/bots/` package with empty `__init__.py`
- [x] 2.2 Create `src/codemoo/core/bots/echo_bot.py` with `EchoBot` using `ClassVar` fields; delete `src/codemoo/core/echo_bot.py`
- [x] 2.3 Create `src/codemoo/core/bots/llm_bot.py` with `LLMBot` as `@dataclass` importing from `core.backend`
- [x] 2.4 Create `src/codemoo/core/bots/chat_bot.py` with `ChatBot` as `@dataclass` delegating to `build_llm_context`
- [x] 2.5 Re-export `EchoBot`, `LLMBot`, `ChatBot` from `core/bots/__init__.py`

## 3. Update participant protocol

- [x] 3.1 Replace `@property` declarations in `ChatParticipant` with plain annotations (`name: str`, `emoji: str`, `is_human: bool`)
- [x] 3.2 Replace `@property` methods on `HumanParticipant` with `ClassVar` fields

## 4. Slim down llm package

- [x] 4.1 Update `src/codemoo/llm/backend.py` to import `Message` and `LLMBackend` from `core.backend`; remove the protocol and `LLMMessage` definitions
- [x] 4.2 Delete `src/codemoo/llm/message.py`
- [x] 4.3 Delete `src/codemoo/llm/bots.py`

## 5. Migrate tests

- [x] 5.1 Create `tests/core/bots/__init__.py`
- [x] 5.2 Move `tests/core/test_echo_bot.py` → `tests/core/bots/test_echo_bot.py`; update import paths
- [x] 5.3 Split `tests/llm/test_bots.py` into `tests/core/bots/test_llm_bot.py` and `tests/core/bots/test_chat_bot.py`; update imports (`LLMMessage` → `Message`, module paths)
- [x] 5.4 Delete `tests/llm/test_bots.py`

## 6. Update dependents and verify

- [x] 6.1 Update any imports in `src/codemoo/chat/` and other modules referencing old paths
- [x] 6.2 Run `uv run pytest` — all tests pass
- [x] 6.3 Run `uv run ruff check .` and `uv run ruff format .` — no errors
- [x] 6.4 Run `uv run ty check` — no type errors
