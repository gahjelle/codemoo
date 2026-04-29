## MODIFIED Requirements

### Requirement: BotVariantConfig carries description, tools, prompts, and instructions
A `BotVariantConfig` Pydantic model SHALL exist with fields `description: str`, `tools: list[str] = []`, `prompts: list[str] = []`, and `instructions: str = ""`. It SHALL use `StrictModel` (extra fields forbidden).

#### Scenario: BotVariantConfig is parsed with all fields
- **WHEN** a variant entry contains `description`, `tools`, `prompts`, and `instructions`
- **THEN** `BotVariantConfig` SHALL parse all four fields correctly

#### Scenario: BotVariantConfig tools, prompts, and instructions default to empty
- **WHEN** a variant entry contains only `description`
- **THEN** `tools` and `prompts` SHALL both equal `[]`, and `instructions` SHALL equal `""`, with no validation error

#### Scenario: BotVariantConfig instructions field carries the system prompt text
- **WHEN** a variant entry contains `instructions = "You are a helpful coding agent."`
- **THEN** `BotVariantConfig.instructions` SHALL equal `"You are a helpful coding agent."`

#### Scenario: Unknown field in BotVariantConfig raises validation error
- **WHEN** a variant entry contains an unrecognised key
- **THEN** Pydantic SHALL raise a validation error

### Requirement: ResolvedBotConfig dataclass merges identity and variant fields including instructions
A `ResolvedBotConfig` dataclass (not a Pydantic model) SHALL carry: `bot_type: BotType`, `name: str`, `emoji: str`, `sources: list[str]`, `description: str`, `tools: list[str]`, `prompts: list[str]`, `instructions: str`. It is produced at runtime and never parsed from TOML.

#### Scenario: ResolvedBotConfig is produced by resolve()
- **WHEN** `resolve(bots_dict, BotRef(type="AgentBot", variant="m365"))` is called
- **THEN** the result SHALL have `bot_type == "AgentBot"`, `name` from `BotConfig`, and `description`/`tools`/`prompts`/`instructions` from the `"m365"` `BotVariantConfig`

#### Scenario: resolve() carries instructions from variant
- **WHEN** `resolve()` is called for a variant with `instructions = "Handle M365 tasks."`
- **THEN** `ResolvedBotConfig.instructions` SHALL equal `"Handle M365 tasks."`

#### Scenario: resolve() carries empty instructions when variant omits the field
- **WHEN** `resolve()` is called for a variant with no `instructions` key
- **THEN** `ResolvedBotConfig.instructions` SHALL equal `""`

#### Scenario: resolve() raises KeyError for unknown variant
- **WHEN** `resolve()` is called with a variant name not present in `BotConfig.variants`
- **THEN** it SHALL raise `KeyError`
