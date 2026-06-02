## 1. Config — progression order and names

- [x] 1.1 In `codemoo.toml` `scripts.all`, swap `GuardBot` and `RetryBot` lines so RetryBot precedes GuardBot
- [x] 1.2 In `codemoo.toml` `scripts.m365`, swap `GuardBot` and `RetryBot` lines
- [x] 1.3 In `codemoo.toml` `scripts.workspace`, swap `GuardBot` and `RetryBot` lines
- [x] 1.4 In `codemoo.toml` `[bots.GuardBot]`, update `name = "Cato"` → `name = "Lock"` (emoji `"LOCK"` unchanged)
- [x] 1.5 In `codemoo.toml` `[bots.RetryBot]`, update `name = "Lava"` → `name = "Crow"` and `emoji = "VOLCANO"` → `emoji = "BIRD"`

## 2. Bot implementations

- [x] 2.1 In `retry_bot.py`, remove the `requires_approval` check, `_ask_fn`, `register_guard`, and all approval-related imports; update module docstring to "RetryBot: full AgentBot feature set with catch_errors=True on all tool calls."
- [x] 2.2 In `guard_bot.py`, add `catch_errors=True` to both `dispatch_tool` call sites (approved path and non-approval path); update module docstring to reflect it is built on RetryBot and passes `catch_errors=True`
- [x] 2.3 In `bots/__init__.py`, swap the `case "GuardBot"` and `case "RetryBot"` blocks in `_make_bot` so RetryBot precedes GuardBot

## 3. Instruction files

- [x] 3.1 In `guard_bot-code.txt`, replace `"You are Cato"` with `"You are Lock"`
- [x] 3.2 In `guard_bot-m365.txt`, replace `"You are Cato"` with `"You are Lock"`
- [x] 3.3 In `guard_bot-workspace.txt`, replace `"You are Cato"` with `"You are Lock"`
- [x] 3.4 In `retry_bot-code.txt`, replace `"You are Lava"` with `"You are Crow"`
- [x] 3.5 In `retry_bot-m365.txt`, replace `"You are Lava"` with `"You are Crow"`
- [x] 3.6 In `retry_bot-workspace.txt`, replace `"You are Lava"` with `"You are Crow"`

## 4. Documentation

- [x] 4.1 In `AGENTS.md` credo table, update `Cato (GuardBot)` → `Lock (GuardBot)` and `Lava (RetryBot)` → `Crow (RetryBot)`
- [x] 4.2 In `AGENTS.md` line referencing `RetryBot (Lava)` in the demo environment section, update to `RetryBot (Crow)`
- [x] 4.3 Review `README.md`, `PLANS.md`, and `BOTS.md` for any references to Cato, Lava, VOLCANO, or the old progression order and update as needed

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 5.2 Run `uv run ty check src/ tests/`
- [x] 5.3 Run `uv run pytest`
- [x] 5.4 Start `uv run codemoo` and verify the bot progression shows Crow before Lock with correct emojis
