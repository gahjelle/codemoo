## MODIFIED Requirements

### Requirement: Default invocation launches chat with hardcoded default bot and variant
When `codemoo` is run with no arguments, the application SHALL launch `ChatApp` with `GuardBot` using variant `"code"`. When `enterproose` is run with no arguments, it SHALL use `GuardBot` with variant `"business"`. These defaults SHALL be expressed as Python default parameter values in `code_chat` and `business_chat` respectively. There SHALL be no `main_bot` config section.

#### Scenario: Bare code invocation uses GuardBot with code variant
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `GuardBot` instance resolved with variant `"code"`

#### Scenario: Bare business invocation uses GuardBot with business variant
- **WHEN** the user runs `enterproose` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `GuardBot` instance resolved with variant `"business"`

#### Scenario: --bot overrides the default bot type
- **WHEN** the user runs `codemoo --bot EchoBot`
- **THEN** `ChatApp` SHALL open with `EchoBot` resolved with the default variant `"code"`

#### Scenario: --variant overrides the default variant
- **WHEN** the user runs `codemoo --variant business`
- **THEN** `ChatApp` SHALL open with `GuardBot` resolved with variant `"business"`

#### Scenario: --bot and --variant together specify a complete BotRef
- **WHEN** the user runs `codemoo --bot AgentBot --variant code`
- **THEN** `ChatApp` SHALL open with an `AgentBot` instance resolved with variant `"code"`

### Requirement: _chat instantiates the specified BotRef directly without loading a script
`_chat()` SHALL construct exactly one bot from the given `bot: BotType` and `variant: str` arguments by creating a `BotRef` and calling `make_bots` with that single ref. It SHALL NOT load a script or use `_default_script_for_mode`. After instantiation, `_chat` SHALL run init hooks for the bot's tools before opening `ChatApp`.

#### Scenario: Single bot is instantiated from BotRef
- **WHEN** `_chat(bot="GuardBot", variant="code")` is called
- **THEN** exactly one bot SHALL be created and passed to `ChatApp`

#### Scenario: Init hooks run before ChatApp opens
- **WHEN** `_chat` is called with a bot that has M365 tools
- **THEN** init hooks SHALL execute (triggering auth if needed) before `ChatApp` is shown

### Requirement: select subcommand is available on both apps and shows full bot catalog
Both `code_app` and `business_app` SHALL register a `select` subcommand. It SHALL build the full catalog of `ResolvedBotConfig` instances from `config.bots` (all types × all variants, in config definition order) and pass it to `SelectionApp`. After the user confirms, init hooks for the selected bots' tools SHALL run before `ChatApp` opens.

#### Scenario: select is available on the code app
- **WHEN** the user runs `codemoo select`
- **THEN** `SelectionApp` SHALL be displayed with the full bot/variant catalog

#### Scenario: select is available on the business app
- **WHEN** the user runs `enterproose select`
- **THEN** `SelectionApp` SHALL be displayed with the full bot/variant catalog

#### Scenario: Full catalog contains all types and variants
- **WHEN** `SelectionApp` is shown
- **THEN** it SHALL include entries for every `(bot_type, variant)` pair present in `config.bots`

#### Scenario: Init hooks run after selection, before chat
- **WHEN** the user confirms a selection that includes M365 bots
- **THEN** auth SHALL be triggered before `ChatApp` opens

### Requirement: demo subcommand accepts --script, --start, and --end; no --mode
`codemoo demo` and `enterproose demo` SHALL accept `--script <name>`, `--start <bot-spec>`, and `--end <bot-spec>`. There SHALL be no `--mode` parameter. `_run_demo` SHALL collect init hooks from all bots in the script and run them before the first slide.

#### Scenario: demo --script selects a named script
- **WHEN** the user runs `codemoo demo --script m365`
- **THEN** the demo SHALL run using the bots listed in the `m365` script

#### Scenario: demo runs init hooks for all script bots before starting
- **WHEN** the user runs `codemoo demo --script m365`
- **THEN** auth (if required) SHALL be triggered before the first `ChatApp` slide opens

#### Scenario: demo with no options uses the default script
- **WHEN** the user runs `codemoo demo` with no arguments
- **THEN** the demo SHALL use the bots from the `"default"` script

### Requirement: list-scripts subcommand shows script name and bots without a Mode column
`codemoo list-scripts` SHALL display a table with columns for script name and bot list. The Mode column SHALL NOT appear.

#### Scenario: list-scripts output has no Mode column
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the table SHALL NOT include a Mode column

## REMOVED Requirements

### Requirement: _chat selects the first script whose mode matches the requested mode
**Reason**: Scripts no longer have a `mode` field. `_chat()` now instantiates the bot directly from `--bot` and `--variant` without loading a script.
**Migration**: Remove `_default_script_for_mode()` and the script-loading path from `_chat()`.

### Requirement: chat command accepts a --mode flag
**Reason**: Mode is removed. Bot and variant together fully specify the desired bot.
**Migration**: Replace `--mode` with `--variant` at call sites.

### Requirement: select command accepts a --mode flag and filters bots by mode
**Reason**: The full catalog is shown regardless of entry point. Mode filtering is no longer meaningful.
**Migration**: Remove `--mode` from `select` subcommand. Both apps show the same catalog.

### Requirement: _setup() accepts a mode parameter
**Reason**: `_setup()` no longer gates M365 auth on mode. Auth is handled by init hooks.
**Migration**: Remove `mode` parameter from `_setup()`. Remove the `if mode == "business"` auth block.
