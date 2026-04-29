## ADDED Requirements

### Requirement: BotVariantConfig carries description, tools, and prompts
A `BotVariantConfig` Pydantic model SHALL exist with fields `description: str`, `tools: list[str] = []`, and `prompts: list[str] = []`. It SHALL use `StrictModel` (extra fields forbidden).

#### Scenario: BotVariantConfig is parsed with all fields
- **WHEN** a variant entry contains `description`, `tools`, and `prompts`
- **THEN** `BotVariantConfig` SHALL parse all three fields correctly

#### Scenario: BotVariantConfig tools and prompts default to empty
- **WHEN** a variant entry contains only `description`
- **THEN** `tools` and `prompts` SHALL both equal `[]` with no validation error

#### Scenario: Unknown field in BotVariantConfig raises validation error
- **WHEN** a variant entry contains an unrecognised key
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotConfig carries name, emoji, sources, and a variants dict — no type field
A `BotConfig` Pydantic model SHALL have fields `name: str`, `emoji: str`, `sources: list[str]`, and `variants: dict[str, BotVariantConfig]`. It SHALL NOT have a `type` field. The emoji field SHALL be validated via Unicode name lookup (unchanged from prior behaviour).

#### Scenario: BotConfig is parsed from TOML with one variant
- **WHEN** a `[bots.EchoBot]` entry has `name`, `emoji`, `sources`, and a `[bots.EchoBot.variants.default]` sub-table
- **THEN** `config.bots["EchoBot"].variants["default"]` SHALL be a valid `BotVariantConfig`

#### Scenario: BotConfig with no type field is accepted
- **WHEN** a bot entry omits the `type` key
- **THEN** no validation error SHALL occur

#### Scenario: BotConfig with a type field is rejected
- **WHEN** a bot entry includes `type = "EchoBot"`
- **THEN** Pydantic SHALL raise a validation error (extra fields forbidden)

#### Scenario: BotConfig with an empty variants dict is rejected
- **WHEN** a bot entry declares `variants = {}`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: CodemooConfig.bots is keyed by BotType
`CodemooConfig.bots` SHALL be typed as `dict[BotType, BotConfig]`. The closed `BotType` Literal covers all valid Python bot class names. Synthetic compound keys (e.g. `"AgentBot_m365"`, `"ScanBot_lite"`) SHALL NOT appear in the bots dict.

#### Scenario: Each BotType appears at most once in config.bots
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots` SHALL have at most one entry per `BotType` value

#### Scenario: An unrecognised bot key raises a validation error
- **WHEN** a `[bots.UnknownBot]` entry appears in TOML
- **THEN** Pydantic SHALL raise a validation error on config load

### Requirement: BotRef carries type and variant fields
A `BotRef` Pydantic model SHALL have fields `type: BotType` and `variant: str`. It SHALL use `StrictModel`.

#### Scenario: BotRef is parsed from an inline table
- **WHEN** `{type = "AgentBot", variant = "m365"}` appears in a script's bots list
- **THEN** the parsed `BotRef` SHALL have `type == "AgentBot"` and `variant == "m365"`

#### Scenario: BotRef with invalid type raises validation error
- **WHEN** `{type = "UnknownBot", variant = "default"}` is parsed
- **THEN** Pydantic SHALL raise a validation error

### Requirement: ResolvedBotConfig dataclass merges identity and variant fields
A `ResolvedBotConfig` dataclass (not a Pydantic model) SHALL carry: `bot_type: BotType`, `name: str`, `emoji: str`, `sources: list[str]`, `description: str`, `tools: list[str]`, `prompts: list[str]`. It is produced at runtime and never parsed from TOML.

#### Scenario: ResolvedBotConfig is produced by resolve()
- **WHEN** `resolve(bots_dict, BotRef(type="AgentBot", variant="m365"))` is called
- **THEN** the result SHALL have `bot_type == "AgentBot"`, `name` from `BotConfig`, and `description`/`tools`/`prompts` from the `"m365"` `BotVariantConfig`

#### Scenario: resolve() raises KeyError for unknown variant
- **WHEN** `resolve()` is called with a variant name not present in `BotConfig.variants`
- **THEN** it SHALL raise `KeyError`
