## 1. Create approval.py

- [x] 1.1 Create `src/codemoo/core/bots/approval.py` with `Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`, `_denial_message`, and `_async_approved`

## 2. Update guard_bot.py

- [x] 2.1 Remove local definitions of `Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`, `_denial_message`, `_async_approved`
- [x] 2.2 Add imports from `codemoo.core.bots.approval`

## 3. Update project_bot.py

- [x] 3.1 Remove local definitions of `Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`, `_denial_message`, `_async_approved`
- [x] 3.2 Add imports from `codemoo.core.bots.approval`

## 4. Update app.py

- [x] 4.1 Redirect `ApprovalRequest` and `GuardDecision` imports from `guard_bot` to `approval`

## 5. Verify

- [x] 5.1 Run `uv run ruff format src/ tests/`
- [x] 5.2 Run `uv run ruff check src/ tests/`
- [x] 5.3 Run `uv run ty check src/ tests/`
- [x] 5.4 Run `uv run pytest`

## 6. Documentation

- [x] 6.1 Review `AGENTS.md`, `PLANS.md`, `BOTS.md`, and `README.md` — update if any references to where approval types are defined need updating
