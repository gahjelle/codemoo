## Why

The `mode` concept (code vs business) currently serves two unrelated purposes: routing M365 authentication and selecting default scripts/bots. This coupling makes it impossible to use a business-variant bot without triggering M365 auth, or to use a code-variant bot in a business app context. Removing `mode` as a first-class concept lets tools self-declare their initialization needs and lets bot/variant pairs stand as the complete specification of a bot.

## What Changes

- **BREAKING** Remove `mode` field from `ScriptConfig` — scripts are now plain lists of `BotRef`
- **BREAKING** Remove `main_bot` from the config schema entirely — defaults are hardcoded in the TUI entry functions
- **BREAKING** Remove `ModeName` type
- **BREAKING** Remove `mode` parameter from `ChatApp`, `BackendStatus`, `code_chat`, `business_chat`
- Add `init: Callable[[], None] | None` field to `ToolDef` — tools declare their own initialization
- Dissolve `make_graph_tools(cfg)` factory — M365 tools become module-level registry entries carrying a shared `_init_m365` init hook; remove `extra_tools` parameter from `make_bots`
- At startup, collect all tools for the bots that will run, deduplicate init hooks by function identity, and execute them — ensures M365 auth prompt appears once, upfront
- `SelectionApp` takes `list[ResolvedBotConfig]` (full catalog from config, in definition order) instead of pre-instantiated bots; bot instantiation and init-hook execution happen after selection
- `BackendStatus` displays active bots as `GuardBot (code) • AgentBot (code) • v2026.x.x` instead of mode label
- Drop `.mode-code` / `.mode-business` CSS background tints
- Add a single `select` command to both `code_app` and `business_app`

## Non-goals

- Merging the two CLI entry points (`codemoo` / `enterproose`) into one
- Changing how demo scripts function (scripts still define ordered bot progressions)
- Changing bot variant names or the variant system itself

## Capabilities

### New Capabilities

- `tool-init-hooks`: ToolDef carries an optional `init` callable; startup logic collects and deduplicates hooks across all bots that will run, then executes them before chat begins

### Modified Capabilities

- `structured-tool-def`: ToolDef gains `init: Callable[[], None] | None = None` field
- `bot-tool-registry`: unified registry includes M365 tools; `make_bots` drops `extra_tools` parameter
- `m365-tool-factory`: factory function dissolved; tools are module-level constants with shared init hook
- `m365-graph-auth`: auth triggered by `_init_m365` init hook execution, not by mode string check
- `demo-scripts`: `ScriptConfig.mode` field removed; scripts are pure `list[BotRef]`
- `frontend-tui`: `code_chat`/`business_chat` gain `variant: str` param and hardcode bot defaults; `--mode` flag removed; `main_bot` config section gone
- `bot-selection-screen`: input changes from `list[ChatParticipant]` to `list[ResolvedBotConfig]`; shows full bot/variant catalog in config order with emoji; init hooks run after selection
- `backend-status-bar`: left label changes from mode string to bot/variant list format
- `mode-background-tint`: spec voided — CSS tints removed entirely
- `mode-status-bar`: replaced by bot/variant display (see `backend-status-bar` delta)

## Impact

- `src/codemoo/config/schema.py` — remove `ModeName`, `ScriptConfig.mode`, `CodemooConfig.main_bot`
- `src/codemoo/core/tools/__init__.py` — add `init` field to `ToolDef`
- `src/codemoo/m365/tools/__init__.py` — dissolve factory; module-level tool constants with `_init_m365`
- `src/codemoo/m365/auth.py` — expose `_init_m365` function
- `src/codemoo/core/bots/__init__.py` — remove `extra_tools` param; add startup init-hook runner
- `src/codemoo/chat/app.py` — remove `mode` param
- `src/codemoo/chat/backend_status.py` — take `list[ResolvedBotConfig]`; new label format
- `src/codemoo/chat/chat.tcss` — remove `.mode-code` / `.mode-business` rules
- `src/codemoo/chat/selection.py` — take `list[ResolvedBotConfig]`; defer instantiation
- `src/codemoo/frontends/tui.py` — remove `_default_script_for_mode`; hardcode defaults; add `select` to both apps
- `codemoo.toml` — remove `[main_bot]` section; remove `mode` from all `[scripts.*]` sections
- Any tests that reference `ModeName`, `mode=`, `main_bot`, or `extra_tools`
