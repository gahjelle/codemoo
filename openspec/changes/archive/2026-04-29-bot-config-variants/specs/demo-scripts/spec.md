## MODIFIED Requirements

### Requirement: [scripts] TOML section defines named structured script objects
The `configs/codemoo.toml` file SHALL contain a `[scripts]` section. Each key SHALL be a script name; its value SHALL be a structured object with `mode: ModeName` and `bots: list[BotRef]`. A `"default"` script SHALL always be present with `mode = "code"` and SHALL list `BotRef` inline tables for the standard coding progression. Each `BotRef` SHALL use `{type = "<BotType>", variant = "<variant>"}` inline-table syntax.

#### Scenario: Default script has mode and bots fields
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.scripts["default"].mode` SHALL equal `"code"` and `config.scripts["default"].bots` SHALL be a list of `BotRef` instances

#### Scenario: Default script lists the coding progression as BotRefs
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts["default"].bots` SHALL contain 9 `BotRef` entries with types `["EchoBot", "LlmBot", "ChatBot", "SystemBot", "ToolBot", "ReadBot", "ChangeBot", "AgentBot", "GuardBot"]` in that order

#### Scenario: m365 script bots reference m365 variants
- **WHEN** `config.scripts["m365"].bots` is accessed
- **THEN** the `AgentBot` and `GuardBot` entries SHALL have `variant == "m365"`

#### Scenario: Additional scripts list a subset of BotRefs
- **WHEN** a script entry such as `focused` is present
- **THEN** `config.scripts["focused"].bots` SHALL be the configured list of `BotRef` instances

### Requirement: make_bots() accepts a bot_refs parameter of type list[BotRef]
`make_bots()` SHALL accept a `bot_refs: list[BotRef]` parameter (replacing `bot_order: list[str]`). It SHALL construct bots in the order given by `bot_refs`.

#### Scenario: make_bots respects BotRef order
- **WHEN** `make_bots(backend, human_name, cfg, bot_refs=[BotRef(type="LlmBot", variant="default"), BotRef(type="AgentBot", variant="code")])` is called
- **THEN** the returned list SHALL contain exactly two bots: an `LlmBot` instance followed by an `AgentBot` instance
