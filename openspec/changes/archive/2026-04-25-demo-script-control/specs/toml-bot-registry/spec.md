## MODIFIED Requirements

### Requirement: make_bots() reads name and emoji from config and respects an explicit bot_order
`make_bots()` SHALL accept a `bot_order: list[BotType]` parameter and construct only the bots listed, in that order, sourcing `name` and `emoji` from `config.bots`. Construction arguments specific to each bot type (backend, tools, human_name) SHALL remain in the `_make_bot()` dispatch helper in Python code.

#### Scenario: Bot name and emoji match TOML values
- **WHEN** `make_bots(backend, human_name, cfg, bot_order=[...])` is called
- **THEN** each returned bot's `.name` and `.emoji` SHALL match the corresponding `config.bots` entry

#### Scenario: make_bots respects the order given in bot_order
- **WHEN** `make_bots(backend, human_name, cfg, bot_order=["AgentBot", "EchoBot"])` is called
- **THEN** the returned list SHALL be `[AgentBot instance, EchoBot instance]` in that order

#### Scenario: make_bots constructs only the bots listed in bot_order
- **WHEN** `make_bots(backend, human_name, cfg, bot_order=["LlmBot"])` is called
- **THEN** the returned list SHALL contain exactly one element of type `LlmBot`

### Requirement: main_bot config field identifies the default chat bot
`CodemooConfig` SHALL include a `main_bot: BotType` field. The TOML config SHALL set `main_bot` to the bot type that should be used when `codemoo` is invoked without `--bot`.

#### Scenario: main_bot is present and valid in the default config
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.main_bot` SHALL be a valid `BotType` string (e.g. `"AgentBot"`)

#### Scenario: Invalid BotType for main_bot raises a validation error
- **WHEN** `main_bot = "UnknownBot"` is set in the TOML
- **THEN** Pydantic SHALL raise a validation error on config load
