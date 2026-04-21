## 1. Protocol Change: Add history to on_message

- [x] 1.1 Update `ChatParticipant` protocol in `codaroo/core/participant.py`: add `history: list[ChatMessage]` parameter to `on_message`
- [x] 1.2 Update `HumanParticipant.on_message` signature to accept and ignore `history`
- [x] 1.3 Update `EchoBot.on_message` signature to accept and ignore `history`
- [x] 1.4 Update all participant tests in `tests/core/` for the new signature

## 2. History Tracking in the Dispatch Shell

- [x] 2.1 Add `self._history: list[ChatMessage]` to `ChatApp.__init__`
- [x] 2.2 Update `_collect_replies` to accept and thread a `running_history` that grows as replies are yielded
- [x] 2.3 Update `on_input_submitted` to append the human message to `self._history` and pass a snapshot to `_collect_replies`
- [x] 2.4 Update `_dispatch` to extend `self._history` with all yielded replies after dispatch completes
- [x] 2.5 Update `tests/chat/test_collect_replies.py` for the new history parameter and behaviour

## 3. New Package: codaroo.llm

- [x] 3.1 Create `src/codaroo/llm/__init__.py`
- [x] 3.2 Implement `LLMMessage` frozen dataclass in `src/codaroo/llm/message.py`
- [x] 3.3 Implement `LLMBackend` protocol and `create_mistral_backend(model)` factory in `src/codaroo/llm/backend.py` (reads `MISTRAL_API_KEY` from env, raises `ValueError` if absent)
- [x] 3.4 Write tests for `LLMMessage` and `create_mistral_backend` error case in `tests/llm/test_backend.py`

## 4. LLMBot Implementation

- [x] 4.1 Implement `LLMBot` in `src/codaroo/llm/bots.py`: accepts `name`, `emoji`, and `backend: LLMBackend`; responds with last message only; skips own messages
- [x] 4.2 Write tests for `LLMBot` in `tests/llm/test_bots.py` using a mock backend (verify single-message context, own-message skip, return value)

## 5. ChatBot Implementation

- [x] 5.1 Implement `ChatBot` in `src/codaroo/llm/bots.py`: accepts `name`, `emoji`, `backend`, `human_name`, and `max_messages=20`; filters and clips history; skips own messages
- [x] 5.2 Write tests for `ChatBot` in `tests/llm/test_bots.py` (verify filtering, role mapping, clipping, current-message appended last, own-message skip)

## 6. Verification

- [x] 6.1 Run `uv run ruff check . && uv run ruff format .` and fix any issues
- [x] 6.2 Run `uv run ty check` and fix any type errors
- [x] 6.3 Run `uv run pytest` and confirm all tests pass
- [x] 6.4 Wire up `LLMBot` or `ChatBot` in the app entry point and smoke-test manually with a real Mistral key
