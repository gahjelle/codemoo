## MODIFIED Requirements

### Requirement: BotVariantConfig carries the preset prompts list
Preset prompts SHALL be defined per variant, not per bot type. Each `BotVariantConfig` entry in TOML MAY include a `prompts: list[str]` field (defaults to `[]`).

#### Scenario: Prompts field is parsed from variant TOML
- **WHEN** a variant entry contains `prompts = ["What is X?", "Explain Y"]`
- **THEN** `config.bots[bot_type].variants[variant].prompts` SHALL equal `["What is X?", "Explain Y"]`

#### Scenario: Missing prompts field on variant defaults to empty list
- **WHEN** a variant entry does not include a `prompts` key
- **THEN** `config.bots[bot_type].variants[variant].prompts` SHALL equal `[]`

### Requirement: DemoContext carries the current bot's prompts sourced from ResolvedBotConfig
When `ChatApp` is launched in demo mode, `DemoContext` SHALL include a `prompts` field initialised from `ResolvedBotConfig.prompts` for the current bot, not from `config.bots[bot_type].prompts`.

#### Scenario: Prompts are populated for a bot with configured prompts in the active variant
- **WHEN** `DemoContext` is constructed for a bot whose resolved config includes prompts
- **THEN** `demo_context.prompts` SHALL equal the list from `ResolvedBotConfig.prompts`

#### Scenario: Prompts are empty for a bot with no prompts in the active variant
- **WHEN** `DemoContext` is constructed for a bot whose resolved variant has no `prompts`
- **THEN** `demo_context.prompts` SHALL be an empty list
