## Why

The TOML config schema and loading infrastructure were added in the previous commit, but the codebase hasn't been wired up to use it fully. Bot names, emojis, descriptions, and source file lists are still hardcoded in Python; only 2 of 8 demo bots are registered; core bots import the config singleton directly (an FC/IS violation); and dead tests reference the deleted `language_instruction()` function.

## What Changes

- Extend `BotType` Literal to all 8 demo bot class names; remove `BotModule` type alias; change `CodemooConfig.bots` to `dict[BotType, BotConfig]`
- Remove `type` field from `BotConfig` (the dict key is the type); add a Pydantic field validator on `emoji` that resolves Unicode names via `unicodedata.lookup()`
- Add all 8 bots to `configs/codemoo.toml`, keyed by class name (e.g. `[bots.EchoBot]`)
- Update `make_bots()` to read `name` and `emoji` from config; keep construction logic in Python (option A)
- Replace hardcoded `_BOTS_DIR` in `slides.py` with `config.paths.bots_dir`; replace `BOT_DESCRIPTIONS`/`BOT_SOURCES` lookups with `config.bots.get(type(bot).__name__)`
- Delete `slides_data.py`
- Add `language: str = "English"` to `ErrorBot` and `CommentatorBot`; remove their `config` imports; inject `language=config.language` from `tui.py`
- Delete `tests/test_config.py`; update `tests/core/bots/test_error_bot.py` to match the injection pattern

## Capabilities

### New Capabilities
- `toml-bot-registry`: All demo bots registered in TOML, keyed by BotType class name, with name, emoji, description, and source file list. Schema validated via Pydantic with emoji Unicode-name resolution.

### Modified Capabilities
- `env-language-config`: `language_instruction()` is removed. Language now comes from `config.language` (TOML with `CODEMOO_LANGUAGE` env override) and is injected into `ErrorBot` and `CommentatorBot` at construction time rather than read from the global config singleton inside core bot methods.
- `demo-bot-descriptions`: Bot descriptions and source file lists move from the hardcoded `slides_data.py` Python dicts to `configs/codemoo.toml`. `slides_data.py` is deleted.

## Impact

- `src/codemoo/config/schema.py` — schema changes
- `configs/codemoo.toml` — add 6 bots, rekey all bots
- `src/codemoo/core/bots/__init__.py` — `make_bots()` reads from config
- `src/codemoo/core/bots/error_bot.py` — language injection
- `src/codemoo/core/bots/commentator_bot.py` — language injection
- `src/codemoo/frontends/tui.py` — inject language at construction
- `src/codemoo/chat/slides.py` — use config for paths, descriptions, sources
- `src/codemoo/chat/slides_data.py` — **deleted**
- `tests/test_config.py` — **deleted**
- `tests/core/bots/test_error_bot.py` — updated
