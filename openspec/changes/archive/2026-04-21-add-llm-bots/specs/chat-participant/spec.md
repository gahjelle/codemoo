## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` property, an `emoji: str` property, an `is_human: bool` property, and an async `on_message(message: ChatMessage, history: list[ChatMessage]) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

## ADDED Requirements

### Requirement: Dispatch shell tracks and injects conversation history
The chat application SHALL maintain a running list of all posted messages and pass it as `history` to every `on_message` call. The `history` list passed to a participant SHALL contain all messages posted before the current `message`; it SHALL NOT include the current `message` itself.

#### Scenario: History is empty on the first message of a session
- **WHEN** the first message of a session is dispatched
- **THEN** every participant SHALL receive an empty `history` list

#### Scenario: History includes all prior messages on subsequent dispatches
- **WHEN** a message is dispatched after one or more prior messages have been posted
- **THEN** every participant SHALL receive a `history` list containing all previously posted messages in chronological order

#### Scenario: History does not include the current message
- **WHEN** `on_message(message, history)` is called
- **THEN** `message` SHALL NOT appear in `history`
