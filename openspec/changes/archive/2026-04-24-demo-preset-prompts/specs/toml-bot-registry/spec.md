## ADDED Requirements

### Requirement: BotConfig carries an optional prompts list
`BotConfig` SHALL include a `prompts` field of type `list[str]` with a default of `[]`. The field SHALL be optional in TOML — omitting it SHALL not cause a validation error.

#### Scenario: BotConfig accepts a prompts list from TOML
- **WHEN** a bot entry includes `prompts = ["Prompt A", "Prompt B"]`
- **THEN** `config.bots[bot_type].prompts` SHALL equal `["Prompt A", "Prompt B"]`

#### Scenario: BotConfig defaults to empty list when prompts is absent
- **WHEN** a bot entry does not include `prompts`
- **THEN** `config.bots[bot_type].prompts` SHALL equal `[]` and no validation error SHALL occur
