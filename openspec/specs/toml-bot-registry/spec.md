# Spec: toml-bot-registry

## Purpose

TBD — defines the TOML-based registry of demo bot types in `configs/codemoo.toml`, including the schema for `BotConfig` entries and how `make_bots()` uses config values for bot construction.

## Requirements

### Requirement: All 8 demo bot types are registered in TOML
The TOML config SHALL contain an entry for every demo bot type: EchoBot, LlmBot, ChatBot, SystemBot, ToolBot, FileBot, ShellBot, AgentBot. Each entry SHALL be keyed by the bot's Python class name.

#### Scenario: All 8 bot types present in config
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.bots` SHALL contain exactly the keys `"EchoBot"`, `"LlmBot"`, `"ChatBot"`, `"SystemBot"`, `"ToolBot"`, `"FileBot"`, `"ShellBot"`, `"AgentBot"`

### Requirement: BotConfig carries name, emoji, description, and sources
Each bot entry in TOML SHALL define `name` (display name), `emoji` (Unicode character name or literal), `description` (one-liner for the slide screen), and `sources` (list of source filenames used in the LLM explanation prompt).

#### Scenario: BotConfig fields are populated for EchoBot
- **WHEN** `config.bots["EchoBot"]` is accessed
- **THEN** `name`, `emoji`, `description`, and `sources` SHALL all be non-empty

#### Scenario: Emoji Unicode name is resolved to character
- **WHEN** a BotConfig is parsed with `emoji = "PARROT"`
- **THEN** `bot_config.emoji` SHALL equal the parrot emoji character `🦜`

#### Scenario: Invalid emoji name raises a validation error
- **WHEN** a BotConfig is parsed with `emoji = "NOT_A_REAL_EMOJI_NAME"`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotType Literal covers all 8 class names; BotModule is removed
The schema SHALL define `BotType` as a `Literal` of the 8 class names. `BotModule` SHALL NOT exist. `BotConfig` SHALL NOT have a `type` field.

#### Scenario: Unknown bot type key is rejected
- **WHEN** a TOML entry with key `"UnknownBot"` is parsed
- **THEN** Pydantic SHALL raise a validation error

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

### Requirement: BotConfig carries an optional prompts list
`BotConfig` SHALL include a `prompts` field of type `list[str]` with a default of `[]`. The field SHALL be optional in TOML — omitting it SHALL not cause a validation error.

#### Scenario: BotConfig accepts a prompts list from TOML
- **WHEN** a bot entry includes `prompts = ["Prompt A", "Prompt B"]`
- **THEN** `config.bots[bot_type].prompts` SHALL equal `["Prompt A", "Prompt B"]`

#### Scenario: BotConfig defaults to empty list when prompts is absent
- **WHEN** a bot entry does not include `prompts`
- **THEN** `config.bots[bot_type].prompts` SHALL equal `[]` and no validation error SHALL occur
