## Context

The TOML config schema and loading pipeline (`configaroo` → Pydantic) were added in the previous commit, but the rest of the codebase still runs on the old patterns: hardcoded bot names/emojis in `make_bots()`, a now-deleted `language_instruction()` function still referenced by tests, and core bot classes importing the config singleton directly instead of receiving config values through constructors.

Two existing specs need to be superseded: `env-language-config` (the `language_instruction()` approach) and `demo-bot-descriptions` (the `slides_data.py` approach).

## Goals / Non-Goals

**Goals:**
- All 8 demo bot types registered in TOML with name, emoji, description, sources
- `make_bots()` reads name/emoji from config; construction logic stays in Python
- `slides.py` drives descriptions, sources, and the bots directory from config; `slides_data.py` deleted
- `language` injected into `ErrorBot`/`CommentatorBot` at construction; no config import in core
- Dead `language_instruction()` tests removed or replaced

**Non-Goals:**
- Full factory construction of bots from TOML (tools lists, human_name, etc.)
- Adding `ErrorBot` or `CommentatorBot` to the TOML registry
- Moving LLM prompt text/instructions to TOML

## Decisions

### Key by BotType (class name), not BotModule (module name)
`[bots.EchoBot]` rather than `[bots.echo_bot]`. The class name is what `slides.py` and `make_bots()` already use to look up bots at runtime (`type(bot).__name__`). Using class names as keys eliminates a module-name→class-name mapping with no added value.

`BotModule` type alias is removed. `BotType` Literal is expanded to all 8 class names. `BotConfig.type` field is removed — the dict key is the type.

### Emoji stored as Unicode name in TOML, resolved by validator
TOML stores `emoji = "PARROT"` and a Pydantic `field_validator` calls `unicodedata.lookup()` to convert to the actual character. If the name is not a valid Unicode character name, the `KeyError` propagates as a Pydantic validation error — no silent fallback. This keeps the TOML readable and ensures typos are caught at startup rather than silently rendering wrong characters.

### Language injected at construction, not read from global config
`ErrorBot(backend=..., language=config.language)` and `CommentatorBot(backend=..., language=config.language)`. Default is `"English"` so tests don't need to supply a config fixture. The shell layer (`tui.py`) is the sole reader of `config.language`; core bots treat it as a plain string.

### `slides_data.py` deleted, not refactored
All data it holds (`BOT_DESCRIPTIONS`, `BOT_SOURCES`) is a strict subset of what `BotConfig` now stores. Keeping both would mean maintaining two sources of truth. `slides.py` looks up descriptions and sources via `config.bots.get(type(bot).__name__)`.

### `_BOTS_DIR` replaced by `config.paths.bots_dir`
The config already carries the resolved absolute path. Using it removes a second hardcoded derivation of the same path.

## Risks / Trade-offs

- **Dict key type safety at runtime**: `config.bots` is `dict[BotType, BotConfig]`. A typo in the TOML key would be caught at parse time by Pydantic's Literal validation — no silent runtime misses.
- **make_bots() still hardcoded for construction**: Adding a new bot type requires editing both the TOML and `make_bots()`. This is acceptable (option A); full TOML-driven construction is a non-goal.
- **slides.py silently falls back when bot not in config**: `config.bots.get(type(bot).__name__)` returns `None` for bots outside the registry (e.g. `ErrorBot`). `_bot_source_block` can fall back to `[f"{classname.lower()}.py"]` and description can fall back to `""`. This is the same behaviour as the current `BOT_SOURCES.get(...)` fallback.

## Migration Plan

No runtime migration needed — all changes are in-process Python and TOML. Tests that import `language_instruction` will fail until this change lands; they are deleted/replaced as part of the same commit.
