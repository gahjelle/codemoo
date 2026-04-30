## 1. Schema

- [x] 1.1 Change `CodemooConfig.main_bot` type from `BotType` to `dict[ModeName, BotRef]` in `src/codemoo/config/schema.py`

## 2. Config

- [x] 2.1 Replace `main_bot = "GuardBot"` in `src/codemoo/config/codemoo.toml` with a `[main_bot]` section containing per-mode inline-table entries: `code = { type = "GuardBot", variant = "code" }` and `business = { type = "GuardBot", variant = "business" }`

## 3. TUI

- [x] 3.1 Add `_default_script_for_mode(mode: ModeName) -> ScriptName` helper to `src/codemoo/frontends/tui.py` that returns the first script name in `config.scripts` whose `mode` matches the argument
- [x] 3.2 Update `_chat()` to call `_default_script_for_mode(mode)` instead of using `script="default"` implicitly
- [x] 3.3 Update `code_chat` and `business_chat` signatures: change `bot: str = config.main_bot` to `bot: BotType = config.main_bot["code"].type` and `bot: BotType = config.main_bot["business"].type` respectively

## 4. Tests

- [x] 4.1 Add tests to `tests/config/test_schema.py` covering the three new `bot-variant-config` scenarios: per-mode table parses correctly, invalid BotType raises, bare string raises
- [x] 4.2 Add tests for `_default_script_for_mode` in a new or existing tui test file: code mode returns first code script, business mode returns first business script, missing mode raises `StopIteration`

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/`
- [x] 5.2 Run `uv run ruff check src/ tests/`
- [x] 5.3 Run `uv run ty check src/ tests/`
- [x] 5.4 Run `uv run pytest`

## 6. Documentation

- [x] 6.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md` and update any references to `main_bot` type or config format if present
