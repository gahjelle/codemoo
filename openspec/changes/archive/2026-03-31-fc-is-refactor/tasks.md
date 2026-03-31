## 1. Create gaia.core package

- [x] 1.1 Create `src/gaia/core/__init__.py`
- [x] 1.2 Move `src/gaia/chat/message.py` → `src/gaia/core/message.py` (no content changes)
- [x] 1.3 Move `src/gaia/chat/participant.py` → `src/gaia/core/participant.py`; add `is_human: bool` to `ChatParticipant` protocol and `HumanParticipant`
- [x] 1.4 Move `src/gaia/chat/echo_bot.py` → `src/gaia/core/echo_bot.py`; remove `datetime.now()` call, use `message.timestamp` for the reply

## 2. Update gaia.chat shell

- [x] 2.1 Update imports in `src/gaia/chat/app.py` to reference `gaia.core.*`
- [x] 2.2 Remove `isinstance(p, HumanParticipant)` from `ChatApp.__init__`; use `p.is_human` instead
- [x] 2.3 Store the human participant as `self._human` in `ChatApp.__init__`; use `self._human.name` in `on_input_submitted`
- [x] 2.4 Extract pure async generator `_collect_replies` from `_dispatch` in `ChatApp`; stamp reply timestamps with `datetime.now(tz=UTC)` inside `_dispatch` before appending to the queue
- [x] 2.5 Remove `src/gaia/chat/message.py`, `src/gaia/chat/participant.py`, `src/gaia/chat/echo_bot.py` (now in core)

## 3. Update entry point and tests

- [x] 3.1 Update imports in `src/gaia/__init__.py` to use `gaia.core.*`
- [x] 3.2 Update imports in `tests/chat/test_message.py`, `test_participant.py`, `test_echo_bot.py` to use `gaia.core.*`
- [x] 3.3 Add test for `EchoBot.on_message` asserting the reply timestamp equals the input timestamp
- [x] 3.4 Add tests for `_collect_replies` covering: single reply, no reply (None), and that the generator does not require a Textual app

## 4. Verification

- [x] 4.1 Run `uv run ruff check .` and `uv run ruff format .` — no errors
- [x] 4.2 Run `uv run ty check` — no type errors
- [x] 4.3 Run `uv run pytest` — all tests pass
- [x] 4.4 Run `uv run gaia` manually and confirm the UI works as before
