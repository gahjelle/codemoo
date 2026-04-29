# Spec: toml-bot-registry

## Purpose

TBD — defines the TOML-based registry of demo bot types in `configs/codemoo.toml`, including the schema for `BotConfig` entries and how `make_bots()` uses config values for bot construction.

## Requirements

### Requirement: All demo bot types are registered in TOML by BotType as the key
The TOML `[bots]` table SHALL contain exactly one entry per `BotType`. The key SHALL be the Python class name (i.e. the `BotType` value). Synthetic compound keys such as `"AgentBot_m365"` or `"ScanBot_lite"` SHALL NOT appear. Bot classes that previously had multiple entries (AgentBot, GuardBot, ScanBot, SendBot) SHALL each have a single entry with multiple named variants.

#### Scenario: All coding bot types present in config
- **WHEN** `configs/codemoo.toml` is loaded and parsed
- **THEN** `config.bots` SHALL contain exactly these keys: `"EchoBot"`, `"LlmBot"`, `"ChatBot"`, `"SystemBot"`, `"ToolBot"`, `"ReadBot"`, `"ChangeBot"`, `"AgentBot"`, `"GuardBot"`, `"ScanBot"`, `"SendBot"`

#### Scenario: No compound bot keys exist
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots` SHALL NOT contain `"AgentBot_m365"`, `"GuardBot_m365"`, `"ScanBot_lite"`, or `"SendBot_lite"`

#### Scenario: AgentBot has both code and m365 variants
- **WHEN** `config.bots["AgentBot"]` is accessed
- **THEN** `config.bots["AgentBot"].variants` SHALL contain keys `"code"` and `"m365"`

### Requirement: BotConfig carries name, emoji, and sources — description and tools are in variants
Each `BotConfig` entry in TOML SHALL define `name`, `emoji`, and `sources`. The `description` and `tools` fields SHALL NOT be top-level on `BotConfig`; they SHALL appear on each `BotVariantConfig` under `variants`.

#### Scenario: BotConfig has no top-level description or tools
- **WHEN** `config.bots["ReadBot"]` is accessed
- **THEN** it SHALL NOT have `.description` or `.tools` attributes

#### Scenario: BotVariantConfig tools field is populated
- **WHEN** `config.bots["ReadBot"].variants["default"]` is accessed
- **THEN** `.tools` SHALL equal `["reverse_string", "read_file", "list_files"]`

#### Scenario: BotVariantConfig tools field is empty for simple bots
- **WHEN** `config.bots["EchoBot"].variants["default"]` is accessed
- **THEN** `.tools` SHALL equal `[]`

#### Scenario: Emoji Unicode name is resolved to character
- **WHEN** a BotConfig is parsed with `emoji = "PARROT"`
- **THEN** `bot_config.emoji` SHALL equal the parrot emoji character `🦜`

#### Scenario: Invalid emoji name raises a validation error
- **WHEN** a BotConfig is parsed with `emoji = "NOT_A_REAL_EMOJI_NAME"`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotVariantConfig instructions field is populated for all bots that use a system prompt
Every bot variant in `configs/codemoo.toml` whose bot class accepts an `instructions` field SHALL declare an `instructions` key. Variants for `EchoBot`, `LlmBot`, and `ChatBot` SHALL omit `instructions` (their bot classes have no such field). `AgentBot` and `GuardBot` SHALL have distinct `instructions` values per variant (`code` vs `m365`).

#### Scenario: AgentBot code and m365 variants have different instructions
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots["AgentBot"].variants["code"].instructions` SHALL differ from `config.bots["AgentBot"].variants["m365"].instructions`
- **AND** both SHALL be non-empty strings

#### Scenario: GuardBot code and m365 variants have different instructions
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots["GuardBot"].variants["code"].instructions` SHALL differ from `config.bots["GuardBot"].variants["m365"].instructions`
- **AND** both SHALL be non-empty strings

#### Scenario: SystemBot default variant has non-empty instructions
- **WHEN** `config.bots["SystemBot"].variants["default"]` is accessed
- **THEN** `.instructions` SHALL be a non-empty string

#### Scenario: EchoBot, LlmBot, ChatBot variants omit instructions
- **WHEN** `config.bots["EchoBot"].variants["default"]` is accessed
- **THEN** `.instructions` SHALL equal `""` (the default; no key in TOML)
- **AND** the same SHALL apply to `LlmBot` and `ChatBot`

### Requirement: make_bots() resolves BotRef objects to ResolvedBotConfig before constructing bots
`make_bots()` SHALL accept `bot_refs: list[BotRef]` instead of `bot_order: list[str]`. For each `BotRef`, it SHALL call `resolve(cfg, ref)` to produce a `ResolvedBotConfig`, then pass it to `_make_bot()`. `_make_bot()` SHALL dispatch on `resolved.bot_type` and source `name`, `emoji`, and `tools` from the resolved config.

#### Scenario: Bot name and emoji match TOML values
- **WHEN** `make_bots()` is called
- **THEN** each returned bot's `.name` and `.emoji` SHALL match the corresponding `BotConfig` entry

#### Scenario: Bot tools match variant tools resolved through registry
- **WHEN** `make_bots()` is called for a BotRef resolving to tools `["read_file", "list_files"]`
- **THEN** the constructed bot SHALL have `tools` equal to the resolved `ToolDef` instances for those names

#### Scenario: make_bots respects BotRef order
- **WHEN** `make_bots()` is called with refs for `[LlmBot/default, AgentBot/code]`
- **THEN** the returned list SHALL contain exactly two bots: an `LlmBot` followed by an `AgentBot`

### Requirement: main_bot config field identifies the default chat bot
`CodemooConfig` SHALL include a `main_bot: BotType` field. The TOML config SHALL set `main_bot` to the bot type that should be used when `codemoo` is invoked without `--bot`.

#### Scenario: main_bot is present and valid in the default config
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.main_bot` SHALL be a valid `BotType` string (e.g. `"AgentBot"`)

#### Scenario: Invalid BotType for main_bot raises a validation error
- **WHEN** `main_bot = "UnknownBot"` is set in the TOML
- **THEN** Pydantic SHALL raise a validation error on config load
