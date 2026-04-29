## REMOVED Requirements

### Requirement: BotConfig carries a required type field constrained to BotType
**Reason**: `BotType` is now the dict key in `CodemooConfig.bots`; a `type` field inside the value is redundant. `BotType` is retained as a type alias used in `BotRef.type`, `CodemooConfig.main_bot`, and `_make_bot()` dispatch.
**Migration**: Remove `type = "..."` from all `[bots.X]` entries in `codemoo.toml`. Remove the `type` field from `BotConfig` in `schema.py`.

### Requirement: BotConfig carries an optional prompts list
**Reason**: Prompts vary per variant and have moved to `BotVariantConfig`. See `demo-preset-prompts` spec.
**Migration**: Remove `prompts` from `BotConfig`. Move prompts to each `[bots.X.variants.Y]` sub-table.

## MODIFIED Requirements

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
