## ADDED Requirements

### Requirement: Core types reside in a dedicated pure package
The system SHALL provide a `gaia.core` package containing only pure types and protocols: `ChatMessage`, `ChatParticipant`, `HumanParticipant`, and `EchoBot`. This package SHALL NOT import from `gaia.chat` or any UI framework.

#### Scenario: Core package has no UI imports
- **WHEN** any module in `gaia.core` is imported
- **THEN** no Textual or other UI framework module SHALL be transitively imported
