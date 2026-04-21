## 1. Core type — ChatMessage default timestamp

- [x] 1.1 Add `from dataclasses import field` import to `message.py`
- [x] 1.2 Change `timestamp: datetime` to `timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))` in `ChatMessage`
- [x] 1.3 Update `tests/core/test_message.py` — ensure tests can construct `ChatMessage` without timestamp, and add a scenario asserting the default is UTC

## 2. Shell — sender-skip and remove re-stamping

- [x] 2.1 In `_collect_replies` (app.py), add `if message.sender == participant.name: continue` before the `on_message` call
- [x] 2.2 Remove the re-stamping block (lines 86–90) that reconstructs `ChatMessage` with a fresh timestamp; replace with direct `queue.append(reply); yield reply`
- [x] 2.3 Remove `from datetime import UTC, datetime` import from `app.py` (no longer needed after removing re-stamping)

## 3. Bots — simplify on_message

- [x] 3.1 `echo_bot.py`: remove `if message.sender == self.name: return None` guard; replace `dataclasses.replace(message, sender=self.name)` with `ChatMessage(sender=self.name, text=message.text)`; add `ChatMessage` import; remove `dataclasses` import
- [x] 3.2 `llm_bot.py`: remove self-sender guard; replace `dataclasses.replace(message, sender=self.name, text=response)` with `ChatMessage(sender=self.name, text=response)`; add `ChatMessage` import; remove `dataclasses` import
- [x] 3.3 `chat_bot.py`: remove self-sender guard; remove explicit `timestamp=datetime.now(tz=UTC)` from the `ChatMessage(...)` construction; remove `from datetime import UTC, datetime` import

## 4. Tests

- [x] 4.1 Update `tests/chat/test_collect_replies.py` — add a test asserting the sender is NOT called back with their own message
- [x] 4.2 Run full test suite (`uv run pytest`) and confirm all tests pass
- [x] 4.3 Run `uv run ruff check .` and `uv run ty check` — fix any issues
