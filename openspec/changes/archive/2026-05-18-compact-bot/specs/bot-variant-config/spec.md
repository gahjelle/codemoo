## ADDED Requirements

### Requirement: BotVariantConfig accepts an optional compact_threshold field
`BotVariantConfig` SHALL accept an optional `compact_threshold: int | None = None` field. When present, the value is the token count at which compaction is triggered for this variant. When absent, the field SHALL default to `None`. The field SHALL be propagated through `ResolvedBotConfig` and passed to `CompactBot` at construction time.

#### Scenario: BotVariantConfig with compact_threshold set
- **WHEN** a variant entry contains `compact_threshold = 8000`
- **THEN** `BotVariantConfig.compact_threshold` SHALL equal `8000`

#### Scenario: BotVariantConfig without compact_threshold defaults to None
- **WHEN** a variant entry omits the `compact_threshold` key
- **THEN** `BotVariantConfig.compact_threshold` SHALL equal `None` with no validation error

## MODIFIED Requirements

### Requirement: BotVariantConfig carries description, tools, prompts, and instructions
A `BotVariantConfig` Pydantic model SHALL exist with fields `description: str`, `tools: list[str] = []`, `prompts: list[str] = []`, `instructions: str = ""`, `memory_file: str | None = None`, and `compact_threshold: int | None = None`. It SHALL use `StrictModel` (extra fields forbidden).

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
