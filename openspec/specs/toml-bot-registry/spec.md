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

### Requirement: make_bots() reads name and emoji from config
`make_bots()` SHALL source each bot's `name` and `emoji` from `config.bots[ClassName]`. Construction arguments specific to each bot type (backend, tools, human_name) SHALL remain in Python code.

#### Scenario: Bot name and emoji match TOML values
- **WHEN** `make_bots(backend, human_name)` is called
- **THEN** each returned bot's `.name` and `.emoji` SHALL match the corresponding `config.bots` entry
