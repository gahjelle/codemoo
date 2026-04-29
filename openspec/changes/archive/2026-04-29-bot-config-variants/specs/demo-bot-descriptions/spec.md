## MODIFIED Requirements

### Requirement: slides.py reads descriptions and source lists from ResolvedBotConfig via DemoContext
`slides.py` SHALL look up bot descriptions and source file lists from `DemoContext.resolved_configs` by index, not by calling `config.bots.get(type(bot).__name__)`. The `cast("BotType", ...)` lookup is eliminated. The fallback for unregistered bot types is no longer needed — every bot in `DemoContext.all_bots` has a corresponding `ResolvedBotConfig` at the same index.

#### Scenario: Description for any registered variant comes from ResolvedBotConfig
- **WHEN** the slide screen renders for the current bot at index N
- **THEN** the description label SHALL display `demo_context.resolved_configs[N].description`

#### Scenario: m365 variant shows its own description
- **WHEN** the slide screen renders for an AgentBot instantiated with the `"m365"` variant
- **THEN** the description SHALL be the m365 variant description, not the code variant description

#### Scenario: Source files for ToolBot include base class file
- **WHEN** the LLM prompt is built for the bot at index N
- **THEN** the prompt SHALL include the contents of all files in `demo_context.resolved_configs[N].sources`
