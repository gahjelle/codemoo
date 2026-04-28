## 1. Fix Event Bubbling in ApprovalModal

- [x] 1.1 In `src/codemoo/chat/approval.py`, add `event.stop()` after `self.dismiss(...)` in `on_input_submitted`

## 2. Strengthen Denial Message in GuardBot

- [x] 2.1 In `src/codemoo/core/bots/guard_bot.py`, update the `_denial_message` return value for `Denied(reason=None)` to `"The user denied this tool call. Do not attempt it again — move on to the next step."`

## 3. Update Tests

- [x] 3.1 Update `tests/core/bots/test_guard_bot.py` to expect the new denial message text for the no-reason case

## 4. Verify

- [x] 4.1 Run `uv run ruff format src/ tests/`
- [x] 4.2 Run `uv run ruff check src/ tests/`
- [x] 4.3 Run `uv run ty check src/ tests/`
- [x] 4.4 Run `uv run pytest`

## 5. Documentation Review

- [x] 5.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md` and update if necessary
