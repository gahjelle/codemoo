## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, and on_message
- **WHEN** an object exposes a `name: str` property, an `emoji: str` property, and an async `on_message(message: ChatMessage) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

## ADDED Requirements

### Requirement: HumanParticipant has fixed display defaults
`HumanParticipant` SHALL have hardcoded defaults for name, emoji, and color class: name `"You"`, emoji `"🧑"`, and CSS class `"bubble--human"`. These SHALL NOT be configurable by the user at this time.

#### Scenario: HumanParticipant exposes fixed name
- **WHEN** `HumanParticipant.name` is accessed
- **THEN** it SHALL return `"You"`

#### Scenario: HumanParticipant exposes fixed emoji
- **WHEN** `HumanParticipant.emoji` is accessed
- **THEN** it SHALL return `"🧑"`
