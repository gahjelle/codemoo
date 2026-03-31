# Spec: chat-participant

## Purpose

Defines the core domain types and protocols for chat participants: an immutable `ChatMessage` value type, a structural `ChatParticipant` protocol, and the rules governing message dispatch and reply propagation within a chat session.

## Requirements

### Requirement: ChatMessage is an immutable value type
The system SHALL represent chat messages as immutable values carrying sender name, message text, and a UTC timestamp.

#### Scenario: Message fields are set at construction
- **WHEN** a `ChatMessage` is created with a sender, text, and timestamp
- **THEN** those fields SHALL be accessible and SHALL NOT be modifiable after construction

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, and on_message
- **WHEN** an object exposes a `name: str` property, an `emoji: str` property, and an async `on_message(message: ChatMessage) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

### Requirement: HumanParticipant has fixed display defaults
`HumanParticipant` SHALL have hardcoded defaults for name, emoji, and color class: name `"You"`, emoji `"🧑"`, and CSS class `"bubble--human"`. These SHALL NOT be configurable by the user at this time.

#### Scenario: HumanParticipant exposes fixed name
- **WHEN** `HumanParticipant.name` is accessed
- **THEN** it SHALL return `"You"`

#### Scenario: HumanParticipant exposes fixed emoji
- **WHEN** `HumanParticipant.emoji` is accessed
- **THEN** it SHALL return `"🧑"`

### Requirement: Participants are notified of every posted message
The system SHALL call `on_message` on every registered participant when any message is posted to the chat, including messages from other participants.

#### Scenario: All participants receive each message
- **WHEN** participant A posts a message
- **THEN** every registered participant (including A) SHALL have `on_message` called with that message

### Requirement: Participant replies are posted to the chat
When a participant's `on_message` returns a `ChatMessage`, the system SHALL post that reply to the chat and propagate it to all participants.

#### Scenario: Non-None reply is appended to the log
- **WHEN** a participant returns a `ChatMessage` from `on_message`
- **THEN** that message SHALL appear in the chat log and trigger another dispatch round

#### Scenario: None reply produces no output
- **WHEN** a participant returns `None` from `on_message`
- **THEN** no additional message SHALL be posted

### Requirement: Participants are registered at session start
The chat session SHALL accept a list of `ChatParticipant` instances at initialisation. The set of participants SHALL NOT change during a session.

#### Scenario: Participants configured before launch
- **WHEN** the chat application starts
- **THEN** all participants SHALL already be registered and ready to receive messages
