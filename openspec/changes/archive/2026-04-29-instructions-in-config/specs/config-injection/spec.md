## MODIFIED Requirements

### Requirement: Config injection in make_bots passes instructions to bots that accept them
The `make_bots()` function SHALL accept cfg parameter containing only the bots configuration section instead of using global config state. `_make_bot()` SHALL pass `instructions=resolved.instructions` to every bot type that declares an `instructions` field (`SystemBot`, `ToolBot`, `ReadBot`, `ChangeBot`, `ScanBot`, `SendBot`, `AgentBot`, `GuardBot`). Bot types without an `instructions` field (`EchoBot`, `LlmBot`, `ChatBot`) SHALL receive no instructions argument.

#### Scenario: make_bots accepts cfg parameter
- **WHEN** `make_bots()` is called with backend, human_name, and cfg parameters
- **THEN** function creates bots using the provided cfg
- **AND** no global config import is used

#### Scenario: Cfg parameter contains bot configurations
- **WHEN** cfg parameter contains bot name and emoji configurations
- **THEN** `make_bots()` uses these values to initialize bot instances
- **AND** bot instances have the names and emojis specified in cfg

#### Scenario: _make_bot passes resolved instructions to AgentBot
- **WHEN** `_make_bot()` constructs an `AgentBot` from a `ResolvedBotConfig` with `instructions = "You are a coding agent."`
- **THEN** the resulting `AgentBot.instructions` SHALL equal `"You are a coding agent."`

#### Scenario: _make_bot passes resolved instructions to SystemBot
- **WHEN** `_make_bot()` constructs a `SystemBot` from a `ResolvedBotConfig` with `instructions = "You are Sona."`
- **THEN** the resulting `SystemBot.instructions` SHALL equal `"You are Sona."`

#### Scenario: _make_bot passes resolved instructions to GuardBot
- **WHEN** `_make_bot()` constructs a `GuardBot` from a `ResolvedBotConfig` with `instructions = "You are a guard."`
- **THEN** the resulting `GuardBot.instructions` SHALL equal `"You are a guard."`

#### Scenario: _make_bot does not pass instructions to ChatBot
- **WHEN** `_make_bot()` constructs a `ChatBot`
- **THEN** `ChatBot` SHALL be constructed without an `instructions` argument
- **AND** `ChatBot` SHALL NOT have an `instructions` attribute

#### Scenario: _make_bot passes empty instructions when variant omits the field
- **WHEN** `_make_bot()` constructs a bot from a `ResolvedBotConfig` with `instructions = ""`
- **THEN** the bot's `instructions` attribute SHALL equal `""`
