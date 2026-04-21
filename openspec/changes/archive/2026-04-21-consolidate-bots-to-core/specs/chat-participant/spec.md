## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, an `is_human: bool` attribute, and an async `on_message(message: ChatMessage, history: list[ChatMessage]) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

### Requirement: HumanParticipant has fixed display defaults
`HumanParticipant` SHALL have hardcoded class-level defaults for name and emoji: name `"You"` and emoji `"🧑"`. These SHALL NOT be configurable by the user at this time.

#### Scenario: HumanParticipant exposes fixed name
- **WHEN** `HumanParticipant.name` is accessed
- **THEN** it SHALL return `"You"`

#### Scenario: HumanParticipant exposes fixed emoji
- **WHEN** `HumanParticipant.emoji` is accessed
- **THEN** it SHALL return `"🧑"`
