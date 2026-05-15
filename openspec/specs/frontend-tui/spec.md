# Spec: frontend-tui

## Purpose

TBD — defines the CLI entry point and startup modes for the `codemoo` command, including the default chat mode, bot selection, and demo progression.

## Requirements

### Requirement: Default invocation launches chat with hardcoded default bot and variant
When `codemoo` is run with no arguments, the application SHALL launch `ChatApp`
with `RetryBot` using variant `"code"`. When `collebra` is run with no arguments,
it SHALL use `RetryBot` with variant `"workspace"`. These defaults SHALL be
expressed as Python default parameter values in `code_chat` and `business_chat`
respectively. There SHALL be no `main_bot` config section.

The entry points `codemoo` and `moo` SHALL be wired to `launcher:main`; the
launcher SHALL show `SplashApp` before delegating to the existing `tui.py`
setup logic. The CLI argument interface (`--bot`, `--variant`) SHALL be
preserved unchanged.

#### Scenario: Bare code invocation uses RetryBot with code variant
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `RetryBot`
  instance resolved with variant `"code"`

#### Scenario: Bare business invocation uses RetryBot with workspace variant
- **WHEN** the user runs `collebra` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `RetryBot`
  instance resolved with variant `"workspace"`

#### Scenario: --bot overrides the default bot type
- **WHEN** the user runs `codemoo --bot EchoBot`
- **THEN** `ChatApp` SHALL open with `EchoBot` resolved with the default
  variant `"code"`

#### Scenario: --variant overrides the default variant
- **WHEN** the user runs `codemoo --variant business`
- **THEN** `ChatApp` SHALL open with `RetryBot` resolved with variant `"business"`

#### Scenario: --bot and --variant together specify a complete BotRef
- **WHEN** the user runs `codemoo --bot AgentBot --variant code`
- **THEN** `ChatApp` SHALL open with an `AgentBot` instance resolved with
  variant `"code"`

#### Scenario: Splash screen is shown before ChatApp
- **WHEN** the user runs `codemoo` (or `moo`, `collebra`, `ebra`)
- **THEN** `SplashApp` SHALL be visible before `ChatApp` appears

#### Scenario: demoo entry point is unaffected
- **WHEN** the user runs `demoo`
- **THEN** no splash screen SHALL appear; the CLI SHALL behave as before

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

### Requirement: list-bots subcommand is registered on the CLI
The `codemoo` command SHALL expose a `list-bots` subcommand alongside `select`, `demo`, and `list-scripts`.

#### Scenario: list-bots subcommand is accessible
- **WHEN** the user runs `codemoo list-bots`
- **THEN** the command SHALL execute the list-bots logic without error

#### Scenario: list-bots appears in help output
- **WHEN** the user runs `codemoo --help`
- **THEN** `list-bots` SHALL appear in the list of available subcommands

### Requirement: list-scripts subcommand is registered on the CLI
The `codemoo` command SHALL expose a `list-scripts` subcommand alongside `list-bots`, `select`, and `demo`.

#### Scenario: list-scripts subcommand is accessible
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the command SHALL execute without error

#### Scenario: list-scripts appears in help output
- **WHEN** the user runs `codemoo --help`
- **THEN** `list-scripts` SHALL appear in the list of available subcommands
