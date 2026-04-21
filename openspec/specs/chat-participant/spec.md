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

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` property, an `emoji: str` property, an `is_human: bool` property, and an async `on_message(message: ChatMessage, history: list[ChatMessage]) -> ChatMessage | None` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

### Requirement: ChatParticipant protocol exposes is_human flag
The `ChatParticipant` protocol SHALL include an `is_human: bool` property. This allows the imperative shell to render bubbles appropriately without inspecting concrete types.

#### Scenario: HumanParticipant.is_human returns True
- **WHEN** `HumanParticipant.is_human` is accessed
- **THEN** it SHALL return `True`

#### Scenario: Non-human participant is_human returns False
- **WHEN** `is_human` is accessed on any non-human participant (e.g. `EchoBot`)
- **THEN** it SHALL return `False`

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
