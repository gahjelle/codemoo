## MODIFIED Requirements

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

#### Scenario: resolve() raises ValueError with helpful message for unknown variant
- **WHEN** `resolve()` is called with a variant name not present in `BotConfig.variants`
- **THEN** it SHALL raise `ValueError` whose message includes the unknown variant name, the bot type, and the available variant names sorted alphabetically

#### Scenario: resolve() error message lists all variants sorted
- **WHEN** a bot has variants `"code"` and `"business"` and `resolve()` is called with variant `"bad"`
- **THEN** the error message SHALL list `"business"` before `"code"` (alphabetical order)
