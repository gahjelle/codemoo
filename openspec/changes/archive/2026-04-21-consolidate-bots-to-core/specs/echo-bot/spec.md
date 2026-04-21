## MODIFIED Requirements

### Requirement: EchoBot has a fixed display name
The `EchoBot` SHALL expose a stable `name` attribute used as the sender field in its replies.

#### Scenario: Name is accessible
- **WHEN** `EchoBot.name` is accessed
- **THEN** it SHALL return a non-empty string identifying the bot
