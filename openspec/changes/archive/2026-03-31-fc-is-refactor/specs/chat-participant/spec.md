## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` property, an `emoji: str` property, an `is_human: bool` property, and an async `on_message(message: ChatMessage) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

## ADDED Requirements

### Requirement: ChatParticipant protocol exposes is_human flag
The `ChatParticipant` protocol SHALL include an `is_human: bool` property. This allows the imperative shell to render bubbles appropriately without inspecting concrete types.

#### Scenario: HumanParticipant.is_human returns True
- **WHEN** `HumanParticipant.is_human` is accessed
- **THEN** it SHALL return `True`

#### Scenario: Non-human participant is_human returns False
- **WHEN** `is_human` is accessed on any non-human participant (e.g. `EchoBot`)
- **THEN** it SHALL return `False`
