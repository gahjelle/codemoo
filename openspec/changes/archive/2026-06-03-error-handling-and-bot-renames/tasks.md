## 1. Exception Hierarchy

- [x] 1.1 Create `src/codemoo/core/exceptions.py` with `CodemooError(Exception)`, `BackendUnavailableError(CodemooError)`, and `ToolError(CodemooError)`
- [x] 1.2 Delete `src/codemoo/llm/exceptions.py`
- [x] 1.3 Update imports in `src/codemoo/llm/google.py`, `ollama.py`, `mistral.py`, `openrouter.py`, `openai.py`, `anthropic.py`, and `factory.py` to import `BackendUnavailableError` from `codemoo.core.exceptions`

## 2. dispatch_tool Changes

- [x] 2.1 Fix the `"Error "` → `"Error: "` prefix check in `dispatch_tool` (bug: error commentary and raise logic never triggered)
- [x] 2.2 Add `catch_errors: bool = False` parameter to `dispatch_tool`
- [x] 2.3 Implement raise path: when `catch_errors=False` and result starts with `"Error: "`, raise `ToolError(result)` without emitting `ToolEvent(outcome="error")`
- [x] 2.4 Implement catch path: when `catch_errors=True` and result starts with `"Error: "`, emit `ToolEvent(outcome="error")` and return the result string

## 3. Bot Updates — Remove Retry Logic, Add catch_errors=True

- [x] 3.1 Remove `_RETRY_BUDGET`, `retry_counts`, retry key check, and `_escalation_message` from `src/codemoo/core/bots/retry_bot.py` and `src/codemoo/core/bots/compact_bot.py`
- [x] 3.2 Add `catch_errors=True` to all `dispatch_tool` calls in `retry_bot.py`
- [x] 3.3 Add `catch_errors=True` to all `dispatch_tool` calls in `src/codemoo/core/bots/compact_bot.py`
- [x] 3.4 Add `catch_errors=True` to all `dispatch_tool` calls in `src/codemoo/core/bots/project_bot.py`
- [x] 3.5 Add `catch_errors=True` to all `dispatch_tool` calls in `src/codemoo/core/bots/memory_bot.py`

## 4. Bot Renames and Progression Reorder

- [x] 4.1 In `codemoo.toml`: rename RetryBot from `Undo` → `Lava` and change emoji from `GAME DIE` → `VOLCANO`
- [x] 4.2 In `codemoo.toml`: rename ProjectBot from `Lore` → `Aria` and change emoji from `OPEN BOOK` → `MICROPHONE`
- [x] 4.3 In `codemoo.toml`: rename MemoryBot from `Aura` → `Ursa` and change emoji from `SMILING FACE WITH HALO` → `BEAR FACE`
- [x] 4.4 In `codemoo.toml`: move RetryBot entry to immediately after GuardBot and before ProjectBot in all three progressions (`default`, `m365`, `workspace` scripts)
- [x] 4.5 In `codemoo.toml`: move the `[bots.RetryBot]` section and all its variant subsections to sit between `[bots.GuardBot]` and `[bots.ProjectBot]` for consistency with the progression order

## 5. Documentation Review

- [x] 5.1 Read `AGENTS.md` and update the credo table (Undo→Lava, Lore→Aria, Aura→Ursa) and any references to old names/emojis
- [x] 5.2 Read `BOTS.md` and update bot names, emojis, and progression descriptions
- [x] 5.3 Read `PLANS.md` and update any references to old bot names or the old progression order
- [x] 5.4 Read `README.md` and update if bot names or progression are referenced

## 6. Verification

- [x] 6.1 Run `uv run ruff format src/ tests/` and fix any formatting issues
- [x] 6.2 Run `uv run ruff check src/ tests/` and fix any lint errors
- [x] 6.3 Run `uv run ty check src/ tests/` and fix any type errors
- [x] 6.4 Run `uv run pytest` and fix any failing tests
- [x] 6.5 Smoke-test: run `uv run codemoo` and confirm RetryBot (Lava, 🌋) loads as default with no errors
