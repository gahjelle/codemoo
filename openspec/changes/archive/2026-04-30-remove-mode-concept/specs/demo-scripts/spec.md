## MODIFIED Requirements

### Requirement: [scripts] TOML section defines named structured script objects
The `configs/codemoo.toml` file SHALL contain a `[scripts]` section. Each key SHALL be a script name; its value SHALL be a structured object with only `bots: list[BotRef]`. The `mode` field SHALL NOT be present on script objects. A `"default"` script SHALL always be present and SHALL list `BotRef` inline tables for the standard coding progression. Each `BotRef` SHALL use `{type = "<BotType>", variant = "<variant>"}` inline-table syntax.

#### Scenario: Default script has bots field and no mode field
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.scripts["default"].bots` SHALL be a list of `BotRef` instances and `config.scripts["default"]` SHALL NOT have a `mode` attribute

#### Scenario: Default script lists the coding progression as BotRefs
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts["default"].bots` SHALL contain 9 `BotRef` entries with types `["EchoBot", "LlmBot", "ChatBot", "SystemBot", "ToolBot", "ReadBot", "ChangeBot", "AgentBot", "GuardBot"]` in that order

#### Scenario: Additional scripts list a subset of BotRefs
- **WHEN** a script entry such as `focused` is present
- **THEN** `config.scripts["focused"].bots` SHALL be the configured list of `BotRef` instances

## REMOVED Requirements

### Requirement: [scripts] TOML section mode field
**Reason**: `ScriptConfig.mode` is removed. Scripts are pure ordered bot lists; authentication requirements are expressed by the tools each bot uses.
**Migration**: Remove the `mode = ...` line from every `[scripts.*]` section in `codemoo.toml`. Update `ScriptConfig` in the Python schema to remove the `mode` field.
