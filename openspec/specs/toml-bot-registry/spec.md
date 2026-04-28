# Spec: toml-bot-registry

## Purpose

TBD — defines the TOML-based registry of demo bot types in `configs/codemoo.toml`, including the schema for `BotConfig` entries and how `make_bots()` uses config values for bot construction.

## Requirements

### Requirement: All demo bot instances are registered in TOML by instance key
The TOML config SHALL contain an entry for every demo bot instance. Instance keys are arbitrary strings (e.g., `ReadBot`, `ScanBot_lite`). Each entry SHALL be keyed by its instance identifier, not necessarily its Python class name.

#### Scenario: All coding bot instances present in config
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.bots` SHALL contain keys for the 9 coding bot instances: `"EchoBot"`, `"LlmBot"`, `"ChatBot"`, `"SystemBot"`, `"ToolBot"`, `"ReadBot"`, `"ChangeBot"`, `"AgentBot"`, `"GuardBot"`

#### Scenario: All M365 bot instances present in config
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.bots` SHALL contain keys for M365 bot instances including `"ScanBot"`, `"ScanBot_lite"`, `"SendBot"`, `"SendBot_lite"`

### Requirement: BotConfig carries name, emoji, description, sources, and tools fields
Each bot entry in TOML SHALL define `name`, `emoji`, `description`, `sources`, and `tools: list[str]`. The `tools` field SHALL list tool names resolvable in `TOOL_REGISTRY`. Bots with no tools (EchoBot, LlmBot, ChatBot, SystemBot) SHALL have `tools = []`.

#### Scenario: BotConfig tools field is populated for ReadBot
- **WHEN** `config.bots["ReadBot"]` is accessed
- **THEN** `config.bots["ReadBot"].tools` SHALL equal `["read_file", "list_files"]`

#### Scenario: BotConfig tools field is empty for EchoBot
- **WHEN** `config.bots["EchoBot"]` is accessed
- **THEN** `config.bots["EchoBot"].tools` SHALL equal `[]`

#### Scenario: Emoji Unicode name is resolved to character
- **WHEN** a BotConfig is parsed with `emoji = "PARROT"`
- **THEN** `bot_config.emoji` SHALL equal the parrot emoji character `🦜`

#### Scenario: Invalid emoji name raises a validation error
- **WHEN** a BotConfig is parsed with `emoji = "NOT_A_REAL_EMOJI_NAME"`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotConfig carries a required type field constrained to BotType
`BotConfig` SHALL include a required `type: BotType` field naming the Python class to instantiate. `BotType` SHALL remain a closed `Literal` enumerating all valid Python bot class names. The outer `CodemooConfig.bots` field SHALL use `dict[str, BotConfig]` with open `str` keys. Every bot entry in TOML MUST declare `type` explicitly — no defaulting.

#### Scenario: BotConfig type must be present in TOML
- **WHEN** a bot entry is parsed without a `type` field
- **THEN** Pydantic SHALL raise a validation error (field is required)

#### Scenario: BotConfig type ScanBot_lite correctly resolves to ScanBot class
- **WHEN** a bot entry `[bots.ScanBot_lite]` with `type = "ScanBot"` is parsed
- **THEN** the resolved type SHALL be `"ScanBot"`, enabling `ScanBot` class instantiation

#### Scenario: Invalid BotType value raises a validation error
- **WHEN** a bot entry has `type = "UnknownBot"`
- **THEN** Pydantic SHALL raise a validation error listing valid BotType values

### Requirement: All 8 demo bot types are registered in TOML by class name as the key
**Reason**: Bot entries are now keyed by arbitrary instance names, not class names. Multiple instances of the same class (e.g., `ScanBot` and `ScanBot_lite`) must coexist. The class is identified by the required `type` field, not the key.
**Migration**: All existing `[bots.X]` entries must add an explicit `type = "X"` field. The outer `CodemooConfig.bots` type changes from `dict[BotType, BotConfig]` to `dict[str, BotConfig]` (open `str` keys, since instance keys are arbitrary). `BotType` itself is retained as a `Literal` but moves inside `BotConfig.type`. Note: `CodemooConfig.scripts` remains `dict[ScriptName, ScriptConfig]` — that key is still a closed `Literal`.

### Requirement: make_bots() reads name, emoji, and tools from config
`make_bots()` SHALL source `name`, `emoji`, and `tools` from `config.bots`. It SHALL resolve tool names through `TOOL_REGISTRY`. Construction arguments specific to each bot type (backend, human_name, commentator) SHALL remain in `_make_bot()`.

#### Scenario: Bot name and emoji match TOML values
- **WHEN** `make_bots()` is called
- **THEN** each returned bot's `.name` and `.emoji` SHALL match the corresponding `config.bots` entry

#### Scenario: Bot tools match TOML tools field resolved through registry
- **WHEN** `make_bots()` is called for a bot with `tools = ["read_file", "list_files"]`
- **THEN** the constructed bot SHALL have `tools` equal to the resolved `ToolDef` instances for those names

### Requirement: Construction arguments specific to each bot type remain in _make_bot() code
**Reason**: Tool lists move to config. Only truly code-specific concerns (backend, human_name, commentator) remain hardcoded in `_make_bot()`.
**Migration**: Remove tool list literals from all `case` arms. Add `tools` field to all bot config entries in TOML.

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
