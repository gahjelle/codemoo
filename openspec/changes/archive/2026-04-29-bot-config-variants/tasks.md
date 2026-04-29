## 1. Schema: Add BotVariantConfig and BotRef, rewrite BotConfig

- [x] 1.1 Add `BotVariantConfig(StrictModel)` with `description: str`, `tools: list[str] = []`, `prompts: list[str] = []`
- [x] 1.2 Replace `BotConfig` fields: remove `type`, `description`, `tools`, `prompts`; add `variants: dict[str, BotVariantConfig]`
- [x] 1.3 Add `BotRef(StrictModel)` with `type: BotType` and `variant: str`
- [x] 1.4 Update `ScriptConfig.bots` from `list[str]` to `list[BotRef]`
- [x] 1.5 Update `CodemooConfig.bots` from `dict[str, BotConfig]` to `dict[BotType, BotConfig]`

## 2. Schema: Add ResolvedBotConfig dataclass and resolve() function

- [x] 2.1 Add `ResolvedBotConfig` dataclass with `bot_type`, `name`, `emoji`, `sources`, `description`, `tools`, `prompts`
- [x] 2.2 Add `resolve(bots: dict[BotType, BotConfig], ref: BotRef) -> ResolvedBotConfig` function in `config/schema.py` (or a sibling module)

## 3. TOML: Migrate [bots] entries to variant structure

- [x] 3.1 Rewrite single-profile bot entries (EchoBot, LlmBot, ChatBot, SystemBot, ToolBot, ReadBot, ChangeBot): remove `type`, add `[bots.X.variants.default]` with `description`, `tools`, `prompts`
- [x] 3.2 Merge `AgentBot` + `AgentBot_m365` into one `[bots.AgentBot]` with `[bots.AgentBot.variants.code]` and `[bots.AgentBot.variants.m365]`
- [x] 3.3 Merge `GuardBot` + `GuardBot_m365` into one `[bots.GuardBot]` with `[bots.GuardBot.variants.code]` and `[bots.GuardBot.variants.m365]`
- [x] 3.4 Merge `ScanBot` + `ScanBot_lite` into one `[bots.ScanBot]` with `[bots.ScanBot.variants.full]` and `[bots.ScanBot.variants.lite]`
- [x] 3.5 Merge `SendBot` + `SendBot_lite` into one `[bots.SendBot]` with `[bots.SendBot.variants.full]` and `[bots.SendBot.variants.lite]`

## 4. TOML: Migrate [scripts] bots lists to BotRef inline tables

- [x] 4.1 Rewrite `[scripts.default].bots` as inline tables: `[{type = "EchoBot", variant = "default"}, ...]`
- [x] 4.2 Rewrite `[scripts.focused].bots`
- [x] 4.3 Rewrite `[scripts.m365].bots` using `"full"` or `"m365"` variants for ScanBot/SendBot/AgentBot/GuardBot
- [x] 4.4 Rewrite `[scripts.m365_lite].bots`

## 5. Runtime: Update make_bots() and _make_bot()

- [x] 5.1 Change `make_bots()` parameter from `bot_order: list[str]` to `bot_refs: list[BotRef]`; call `resolve()` for each ref before constructing
- [x] 5.2 Change `_make_bot()` parameter from `cfg: BotConfig` to `resolved: ResolvedBotConfig`; dispatch on `resolved.bot_type`
- [x] 5.3 Update `make_bots()` to return resolved configs alongside bots (or return them as a parallel list for use by slides)
- [x] 5.4 Update `tui.py` call sites: pass `config.scripts[script].bots` (now `list[BotRef]`) instead of string lists

## 6. Fix slides.py

- [x] 6.1 Add `resolved_configs: list[ResolvedBotConfig]` to `DemoContext`
- [x] 6.2 Rewrite `_bot_source_block()` to read from `DemoContext.resolved_configs[index]` instead of `config.bots.get(...)`
- [x] 6.3 Rewrite `SlideContent.compose()` to read description from `DemoContext.resolved_configs[index]`
- [x] 6.4 Update `tui.py` to populate `DemoContext.resolved_configs` from the resolved configs returned by `make_bots()`
- [x] 6.5 Remove the `cast("BotType", ...)` import and usage from `slides.py`

## 7. Tests and verification

- [x] 7.1 Update any tests that construct `BotConfig` directly (add `variants`, remove `type`/`description`/`tools`/`prompts` from top level)
- [x] 7.2 Update any tests that reference `ScriptConfig.bots` as `list[str]`
- [x] 7.3 Add tests for `resolve()`: valid ref, unknown variant, unknown bot type
- [x] 7.4 Run `uv run ruff format src/ tests/`
- [x] 7.5 Run `uv run ruff check src/ tests/`
- [x] 7.6 Run `uv run ty check src/ tests/`
- [x] 7.7 Run `uv run pytest`

## 8. Documentation

- [x] 8.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md` and update any references to `BotConfig.type`, compound bot keys, or `ScriptConfig.bots: list[str]`
