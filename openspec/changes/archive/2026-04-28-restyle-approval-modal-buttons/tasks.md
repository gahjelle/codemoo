## 1. Restyle Buttons in ApprovalModal

- [x] 1.1 In `src/codemoo/chat/approval.py`, update `compose()`: change button labels to "Yes", "No, but …", "No"; reorder to Yes / No, but … / No; add `variant="warning"` to the "No, but …" button
- [x] 1.2 In `src/codemoo/chat/approval.py`, add `on_key()` to handle left/right arrow keys while the button row is visible: move focus between the three buttons in order, wrapping at each end

## 2. Verify

- [x] 2.1 Run `uv run ruff format src/ tests/`
- [x] 2.2 Run `uv run ruff check src/ tests/`
- [x] 2.3 Run `uv run ty check src/ tests/`
- [x] 2.4 Run `uv run pytest`

## 3. Documentation Review

- [x] 3.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md` and update if necessary
