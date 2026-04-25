## 1. Config Schema

- [x] 1.1 Add `ScriptName` Literal type alias to `config/schema.py` (initially `Literal["default"]`)
- [x] 1.2 Add `scripts: dict[ScriptName, list[BotType]]` field to `CodemooConfig` in `config/schema.py`
- [x] 1.3 Add `main_bot: BotType` field to `CodemooConfig` in `config/schema.py`
- [x] 1.4 Add `[scripts]` section to `configs/codemoo.toml` with the `"default"` script listing all 8 bots in standard order
- [x] 1.5 Add `main_bot = "AgentBot"` to `configs/codemoo.toml`

## 2. Bot Construction Refactor

- [x] 2.1 Implement `_make_bot(bot_type, cfg, backend, human_name, commentator)` with a match statement dispatching each `BotType` to its constructor, with inline tool lists per case arm
- [x] 2.2 Rewrite `make_bots()` to accept `bot_order: list[BotType]` and return `[_make_bot(t, ...) for t in bot_order]`

## 3. Default Chat Command Update

- [x] 3.1 Update `chat()` in `frontends/tui.py` to use `resolve_bot(config.main_bot, available)` instead of `available[-1]` when `--bot` is not provided

## 4. Demo Command Updates

- [x] 4.1 Add `--script` and `--end` parameters to `demo()` in `frontends/tui.py`
- [x] 4.2 Update `_run_demo()` to resolve the script from config, call `make_bots()` with the script's `bot_order`, then apply `--start` and `--end` slicing against the script-filtered list
- [x] 4.3 Ensure `resolve_bot()` errors for `--start`/`--end` specs that are not in the script's bot list (this follows naturally from passing the filtered list — verify the error message is descriptive)

## 5. list-scripts Command

- [x] 5.1 Implement `list_scripts()` command function in `frontends/tui.py` that prints a Rich table with `Script` and `Bots` columns
- [x] 5.2 Register `list_scripts` as a `@app.command` alongside `list_bots`

## 6. Additional Script

- [x] 6.1 Add `"focused"` to the `ScriptName` Literal in `config/schema.py`
- [x] 6.2 Add `focused = ["LlmBot", "ChatBot", "AgentBot"]` to the `[scripts]` section in `configs/codemoo.toml`
