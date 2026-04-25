## MODIFIED Requirements

### Requirement: Default invocation launches chat with the bot specified by main_bot config
When `codemoo` is run with no arguments, the application SHALL launch `ChatApp` with the bot whose type matches `config.main_bot`, resolved from the available bot list.

#### Scenario: Bare invocation uses main_bot from config
- **WHEN** the user runs `codemoo` with no arguments and `config.main_bot` is `"AgentBot"`
- **THEN** `ChatApp` SHALL open with the human participant and the `AgentBot` instance

#### Scenario: --bot overrides main_bot
- **WHEN** the user runs `codemoo --bot EchoBot`
- **THEN** `ChatApp` SHALL open with `EchoBot`, regardless of `config.main_bot`

### Requirement: demo subcommand accepts --script, --start, and --end options
`codemoo demo` SHALL accept three optional keyword arguments: `--script <name>` (defaults to `"default"`), `--start <bot-spec>`, and `--end <bot-spec>`. All three are optional and may be combined.

#### Scenario: demo --script selects a named script
- **WHEN** the user runs `codemoo demo --script focused`
- **THEN** the demo SHALL run using only the bots listed in the `focused` script

#### Scenario: demo --end selects the last bot inclusive
- **WHEN** the user runs `codemoo demo --end ChatBot`
- **THEN** the demo SHALL run all bots in the default script up to and including ChatBot

#### Scenario: demo --script combined with --start and --end
- **WHEN** the user runs `codemoo demo --script focused --start LlmBot --end ChatBot`
- **THEN** the demo SHALL run exactly the bots between LlmBot and ChatBot in the focused script (inclusive)

#### Scenario: demo with no options uses the default script from first to last bot
- **WHEN** the user runs `codemoo demo` with no arguments
- **THEN** `ChatApp` SHALL open with the first bot in the `"default"` script (EchoBot/Coco)

#### Scenario: demo --script with invalid script name is rejected
- **WHEN** the user runs `codemoo demo --script nonexistent`
- **THEN** cyclopts SHALL reject the argument and list valid script names

## ADDED Requirements

### Requirement: list-scripts subcommand is registered on the CLI
The `codemoo` command SHALL expose a `list-scripts` subcommand alongside `list-bots`, `select`, and `demo`.

#### Scenario: list-scripts subcommand is accessible
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the command SHALL execute without error

#### Scenario: list-scripts appears in help output
- **WHEN** the user runs `codemoo --help`
- **THEN** `list-scripts` SHALL appear in the list of available subcommands
