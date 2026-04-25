## Why

The demo progression is currently all-or-nothing: `--start` lets you skip early bots, but there is no way to limit which bots appear, no named subsets for common presentation scenarios, and no way to stop before the final bot. As the bot catalog grows, presenters need finer control over the agenda without resorting to manual index arithmetic.

## What Changes

- Add a `[scripts]` section to `configs/codemoo.toml` with a `ScriptName` Literal type in the config schema, enabling named, ordered bot subsets
- Add a `"default"` script that lists all 8 bots in the current order — this replaces the implicit hardcoded order in `make_bots()`
- Refactor `make_bots()` to accept an explicit `bot_order: list[BotType]` parameter; extract a `_make_bot()` per-type dispatch helper so bot construction is driven by the script list
- Add `--script <name>` option to `codemoo demo` (optional, defaults to `"default"`)
- Add `--end <bot-spec>` option to `codemoo demo` that sets the last bot (inclusive); resolves against the script's filtered list
- `--start` now resolves against the script's filtered list; numerical indices are script-relative
- Add `codemoo list-scripts` subcommand showing each script name and its ordered bot list
- Add `main_bot = "AgentBot"` to `configs/codemoo.toml` and a `main_bot: BotType` field to the config schema, making the default chat bot an explicit config value rather than an implicit last-in-list convention

## Capabilities

### New Capabilities

- `demo-scripts`: The `[scripts]` TOML config section, `ScriptName` Literal type, and the `make_bots()` / `_make_bot()` refactor that enables script-driven bot construction
- `list-scripts-command`: The `codemoo list-scripts` CLI subcommand

### Modified Capabilities

- `demo-mode`: `--start` and new `--end` both resolve within the script-filtered list; numerical indices are script-relative; the demo operates on the script's ordered bot subset
- `frontend-tui`: `codemoo demo` gains `--script` and `--end` options; `list-scripts` subcommand is registered alongside `list-bots`
- `toml-bot-registry`: `make_bots()` signature changes to accept `bot_order: list[BotType]`; the hardcoded construction order is removed; `main_bot: BotType` field added to schema
- `frontend-tui` (default chat): `codemoo` uses `config.main_bot` instead of `available[-1]` to select the default bot

## Non-goals

- Runtime script editing or creation (scripts are developer-authored TOML, not user configuration)
- Randomisation or non-linear bot ordering beyond what a script defines

## Impact

- `configs/codemoo.toml`: new `[scripts]` section
- `src/codemoo/config/schema.py`: new `ScriptName` Literal; new `scripts` and `main_bot` fields on `CodemooConfig`
- `src/codemoo/core/bots/__init__.py`: `make_bots()` signature change; new `_make_bot()` helper; module-level tool-set constants
- `src/codemoo/frontends/tui.py`: `demo()` and `_run_demo()` updated; `list_scripts()` command added
