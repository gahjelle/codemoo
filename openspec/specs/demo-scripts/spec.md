# Spec: demo-scripts

## Purpose

TBD — defines the `[scripts]` TOML section and associated config schema that allows named, ordered subsets of bots to be selected for a demo session.

## Requirements

### Requirement: [scripts] TOML section defines named ordered bot subsets
The `configs/codemoo.toml` file SHALL contain a `[scripts]` section. Each key in that section is a script name; its value is an ordered list of `BotType` strings. A `"default"` script SHALL always be present and SHALL list all 8 bot types in the standard progression order.

#### Scenario: Default script is present and lists all bots
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.scripts["default"]` SHALL equal `["EchoBot", "LlmBot", "ChatBot", "SystemBot", "ToolBot", "FileBot", "ShellBot", "AgentBot"]`

#### Scenario: Additional scripts list a subset of bots
- **WHEN** a script entry such as `focused = ["LlmBot", "ChatBot", "AgentBot"]` is present
- **THEN** `config.scripts["focused"]` SHALL equal `["LlmBot", "ChatBot", "AgentBot"]`

#### Scenario: Unknown BotType in a script raises a validation error
- **WHEN** a script entry contains a string that is not a valid `BotType` (e.g. `"UnknownBot"`)
- **THEN** Pydantic SHALL raise a validation error on config load

#### Scenario: Missing "default" script raises a validation error
- **WHEN** `configs/codemoo.toml` is loaded and the `[scripts]` section does not contain a `"default"` key
- **THEN** Pydantic SHALL raise a validation error

### Requirement: ScriptName is a Literal type alias covering all configured script names
The config schema SHALL define `type ScriptName = Literal[...]` enumerating all valid script name strings. Adding a new script requires updating both the Literal and the TOML.

#### Scenario: Valid script name is accepted by the type
- **WHEN** `"default"` or another name present in the `ScriptName` Literal is used as a `--script` argument
- **THEN** cyclopts SHALL accept the value without error

#### Scenario: Invalid script name is rejected by the parser
- **WHEN** a string not present in the `ScriptName` Literal is passed as `--script`
- **THEN** cyclopts SHALL reject the argument and print the valid choices

### Requirement: make_bots() accepts an explicit bot_order parameter
`make_bots()` SHALL accept a `bot_order: list[BotType]` parameter and construct only the bots listed, in that order. A private `_make_bot()` helper SHALL dispatch construction by bot type using a match statement.

#### Scenario: make_bots respects script order
- **WHEN** `make_bots(backend, human_name, cfg, bot_order=["LlmBot", "AgentBot"])` is called
- **THEN** the returned list SHALL contain exactly two bots: an `LlmBot` instance followed by an `AgentBot` instance

#### Scenario: _make_bot raises for unhandled bot type
- **WHEN** `_make_bot` is called with a `BotType` value that has no match arm
- **THEN** it SHALL raise `ValueError` with a descriptive message

### Requirement: Tool sets are written inline per bot type in _make_bot()
Each bot's tool list SHALL be written as an inline literal in its `case` arm inside `_make_bot()`. No module-level constants or shared references SHALL be used; the walrus operator coupling between ShellBot and AgentBot SHALL be removed.

#### Scenario: ShellBot and AgentBot tool lists are independent inline literals
- **WHEN** reading the ShellBot and AgentBot case arms in `_make_bot()`
- **THEN** each SHALL have its own explicit list literal with no shared reference between them
