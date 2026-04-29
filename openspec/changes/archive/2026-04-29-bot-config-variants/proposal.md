## Why

Bot entries in `codemoo.toml` conflate two orthogonal things — which bot *class* to use and which configuration *profile* to apply — by encoding both in a synthetic dict key like `"AgentBot_m365"`. This duplicates `name`, `emoji`, `sources`, and `type` across every profile of the same class, and makes it impossible at runtime to know which profile a bot was instantiated from (causing a latent bug in `slides.py` where m365 demo slides always show the coding profile's description).

## What Changes

- **BREAKING** `BotConfig` loses its `type` field; the dict key in `[bots]` becomes the `BotType` identity.
- **BREAKING** `BotConfig` gains a `variants: dict[str, BotVariantConfig]` field. `description`, `tools`, and `prompts` move into `BotVariantConfig` and are no longer top-level `BotConfig` fields.
- **BREAKING** `ScriptConfig.bots` changes from `list[str]` (bot instance keys) to `list[BotRef]`, where `BotRef` carries `type: BotType` and `variant: str`.
- `CodemooConfig.bots` changes from `dict[str, BotConfig]` (open string keys) to `dict[BotType, BotConfig]` (closed BotType keys).
- Synthetic compound bot keys (`"AgentBot_m365"`, `"GuardBot_m365"`, `"ScanBot_lite"`, `"SendBot_lite"`) are eliminated; each class has one entry with multiple named variants.
- A `ResolvedBotConfig` dataclass is introduced for runtime use, merging `BotConfig` + `BotVariantConfig` + the resolved `BotType` key.
- `make_bots()` resolves each `BotRef` to a `ResolvedBotConfig` before constructing bots.
- `DemoContext` gains a `resolved_configs: list[ResolvedBotConfig]` field; `slides.py` reads description and sources from it by index instead of doing a class-name lookup into `config.bots`.

## Non-goals

- No changes to how bot classes (`AgentBot`, `GuardBot`, etc.) are implemented.
- No changes to the tool registry or how tools are defined.
- No new demo scripts or bot types.
- No changes to `ModeName`, `ScriptName`, or the backend configuration structure.

## Capabilities

### New Capabilities

- `bot-variant-config`: `BotVariantConfig` model and the two-level `BotConfig` structure (identity + variants). Covers `BotRef`, `ResolvedBotConfig`, and the `resolve()` function that merges them.

### Modified Capabilities

- `toml-bot-registry`: `BotConfig` loses `type`, gains `variants`; `CodemooConfig.bots` key type narrows from `str` to `BotType`; synthetic compound keys removed.
- `demo-scripts`: `ScriptConfig.bots` changes from `list[str]` to `list[BotRef]`; TOML inline-table syntax.
- `demo-bot-descriptions`: Descriptions move from `BotConfig` to `BotVariantConfig`; slides read description from `ResolvedBotConfig` via `DemoContext`.
- `demo-preset-prompts`: Prompts move from `BotConfig` to `BotVariantConfig`; slide prompt lookup unchanged in behaviour but reads from resolved config.

## Impact

- `src/codemoo/config/schema.py` — schema changes
- `configs/codemoo.toml` — structural rewrite of `[bots]` and `[scripts]` sections
- `src/codemoo/core/bots/__init__.py` — `make_bots()` and `_make_bot()` signatures
- `src/codemoo/chat/slides.py` — `DemoContext`, `_bot_source_block()`, `SlideContent.compose()`
- `src/codemoo/frontends/tui.py` — call sites for `make_bots()` and `DemoContext`
- All tests touching `BotConfig`, `ScriptConfig`, or `make_bots()`
