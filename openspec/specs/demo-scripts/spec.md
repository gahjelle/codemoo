# Spec: demo-scripts

## Purpose

TBD — defines the `[scripts]` TOML section and associated config schema that allows named, ordered subsets of bots to be selected for a demo session.

## Requirements

### Requirement: [scripts] TOML section defines named structured script objects
The `configs/codemoo.toml` file SHALL contain a `[scripts]` section. Each key in that section is a script name; its value SHALL be a structured object with `mode: Literal["code", "m365"]` and `bots: list[str]`. A `"default"` script SHALL always be present with `mode = "code"` and SHALL list the 9 bot instance keys in the standard coding progression order.

#### Scenario: Default script has mode and bots fields
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.scripts["default"].mode` SHALL equal `"code"` and `config.scripts["default"].bots` SHALL be a list of bot instance key strings

#### Scenario: Default script lists the coding progression bots
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts["default"].bots` SHALL contain the 9 coding bot instance keys: `["EchoBot", "LlmBot", "ChatBot", "SystemBot", "ToolBot", "ReadBot", "ChangeBot", "AgentBot", "GuardBot"]`

#### Scenario: m365 script has mode "m365"
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts["m365"].mode` SHALL equal `"m365"`

#### Scenario: Additional scripts list a subset of bots
- **WHEN** a script entry such as `focused` is present with a bots list
- **THEN** `config.scripts["focused"].bots` SHALL be the configured list of bot instance keys

### Requirement: ScriptName is a Literal type alias covering all configured script names
`ScriptName` SHALL remain a closed `Literal` type alias. It SHALL be updated to include all script names: `Literal["default", "focused", "m365", "m365_lite"]`. A new `ModeName = Literal["code", "m365"]` type alias SHALL be added alongside it. Adding a new script requires updating both the `ScriptName` Literal and the TOML.

#### Scenario: Valid script name is accepted by the CLI
- **WHEN** `"default"`, `"m365"`, or `"m365_lite"` is passed as `--script`
- **THEN** cyclopts SHALL accept the value without error

#### Scenario: Invalid script name is rejected by the CLI
- **WHEN** a string not present in `ScriptName` is passed as `--script`
- **THEN** cyclopts SHALL reject the argument and display the valid choices

#### Scenario: ModeName type alias is used wherever mode is typed
- **WHEN** `mode` appears as a parameter in `ScriptConfig`, `_setup()`, `_make_bot()`, or CLI commands
- **THEN** its type annotation SHALL be `ModeName`, not a bare `Literal["code", "m365"]` inline

### Requirement: make_bots() accepts an explicit bot_order parameter
`make_bots()` SHALL accept a `bot_order: list[BotType]` parameter and construct only the bots listed, in that order. A private `_make_bot()` helper SHALL dispatch construction by bot type using a match statement.

#### Scenario: make_bots respects script order
- **WHEN** `make_bots(backend, human_name, cfg, bot_order=["LlmBot", "AgentBot"])` is called
- **THEN** the returned list SHALL contain exactly two bots: an `LlmBot` instance followed by an `AgentBot` instance

#### Scenario: _make_bot raises for unhandled bot type
- **WHEN** `_make_bot` is called with a `BotType` value that has no match arm
- **THEN** it SHALL raise `ValueError` with a descriptive message

### Requirement: [scripts] TOML section values are bare lists of BotType strings
**Reason**: Scripts now carry a `mode` field alongside the bot list. Bare lists cannot represent structured config objects.
**Migration**: All existing script entries must be converted to structured objects with `mode` and `bots` fields. Example: `default = ["EchoBot", ...]` becomes `[scripts.default]` with `mode = "code"` and `bots = [...]`.

### Requirement: Tool sets are written inline per bot type in _make_bot()
**Reason**: Tools move to config and are resolved via TOOL_REGISTRY. Inline tool lists in `_make_bot()` are replaced by `cfg.tools` resolution.
**Migration**: Remove inline tool list literals from all `case` arms in `_make_bot()`. Add `tools` fields to all tool-using bot entries in `codemoo.toml`.
