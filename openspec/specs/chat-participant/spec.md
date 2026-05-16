# Spec: chat-participant

## Purpose

Defines the core domain types and protocols for chat participants: an immutable `ChatMessage` value type, a structural `ChatParticipant` protocol, and the rules governing message dispatch and reply propagation within a chat session.

## Requirements

### Requirement: ChatMessage is an immutable value type
The system SHALL represent chat messages as immutable values carrying sender name, message text, and a UTC timestamp. The `timestamp` field SHALL have a default factory of `datetime.now(UTC)` so that callers may omit it; when omitted the timestamp SHALL be set to the current UTC time at construction.

#### Scenario: Message fields are set at construction
- **WHEN** a `ChatMessage` is created with a sender, text, and timestamp
- **THEN** those fields SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: Timestamp defaults to current UTC time when omitted
- **WHEN** a `ChatMessage` is created with only `sender` and `text`
- **THEN** `timestamp` SHALL be a `datetime` in UTC representing approximately the time of construction

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, and an async `on_message(context: list[ContextItem]) -> list[ContextItem]` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

#### Scenario: Bot with a text reply ends its list with AssistantMessageContent
- **WHEN** a bot participant returns from `on_message`
- **THEN** if it has a text reply, the last item in the returned list SHALL have `content` of type `AssistantMessageContent`

#### Scenario: Bot with no reply returns an empty list
- **WHEN** a participant has no reply (e.g. `ErrorBot`)
- **THEN** `on_message` SHALL return `[]`

### Requirement: HumanParticipant has fixed display defaults
`HumanParticipant` SHALL be a plain dataclass carrying display metadata only: name `"You"` and emoji `"🧑"`. It SHALL NOT implement `on_message` and SHALL NOT satisfy the `ChatParticipant` protocol. It is passed to `ChatApp` as a separate argument alongside the bot participants list.

#### Scenario: HumanParticipant exposes fixed name
- **WHEN** `HumanParticipant.name` is accessed
- **THEN** it SHALL return `"You"`

#### Scenario: HumanParticipant exposes fixed emoji
- **WHEN** `HumanParticipant.emoji` is accessed
- **THEN** it SHALL return `"🧑"`

### Requirement: Participants are notified of every posted message
The system SHALL call `on_message` on every registered participant when any message is posted to the chat, **except** the participant whose `name` matches the message sender. The dispatch shell SHALL enforce this invariant; individual participants SHALL NOT be required to guard against receiving their own messages.

#### Scenario: Sender is skipped during dispatch
- **WHEN** participant A posts a message
- **THEN** `on_message` SHALL NOT be called on participant A for that message
- **THEN** every other registered participant SHALL have `on_message` called with that message

#### Scenario: Other participants receive each message
- **WHEN** participant A posts a message
- **THEN** every participant whose `name` differs from the message sender SHALL have `on_message` called

### Requirement: Participant replies are posted to the chat
When a participant's `on_message` returns a non-empty list whose last item is an `AssistantMessageContent`, the app SHALL derive a `ChatMessage` from that item and post it to the chat log, then propagate it to all participants. If `on_message` raises an exception, the dispatch loop SHALL catch it, yield an error message via `ErrorBot`, and continue processing remaining participants.

#### Scenario: AssistantMessageContent last item produces a chat bubble
- **WHEN** a participant returns a non-empty list with an `AssistantMessageContent` as the last item
- **THEN** a `ChatMessage` SHALL be derived with `sender=participant.name` and `text=last_item.content.text`, posted to the log, and queued for further dispatch

#### Scenario: Empty list produces no output
- **WHEN** a participant returns `[]` from `on_message`
- **THEN** no additional message SHALL be posted

#### Scenario: Exception does not crash the dispatch loop
- **WHEN** a participant's `on_message` raises an exception
- **THEN** the dispatch loop SHALL catch the exception, yield an `ErrorBot` error message, and continue with the remaining participants in the current dispatch round

### Requirement: Participants are registered at session start
The chat session SHALL accept a list of `ChatParticipant` instances at initialisation. The set of participants SHALL NOT change during a session.

#### Scenario: Participants configured before launch
- **WHEN** the chat application starts
- **THEN** all participants SHALL already be registered and ready to receive messages

### Requirement: Dispatch shell tracks and injects conversation history
The chat application SHALL maintain a running list of `ContextItem` values and pass it as `context` to every `on_message` call. The dispatch shell SHALL append the triggering message as a `ContextItem` to `context` **before** calling `on_message`, so that `context[-1]` is always the item corresponding to the triggering message. This is a load-bearing precondition: bots MAY read `context[-1]` to access the triggering message and SHALL NOT be called with an empty `context`.

#### Scenario: Triggering message is last in context on first dispatch
- **WHEN** the first message of a session is dispatched
- **THEN** every participant SHALL receive a `context` list containing exactly one item — the triggering message as a `UserMessageContent`

#### Scenario: Triggering message is last in context on subsequent dispatches
- **WHEN** a message is dispatched after prior turns have been recorded
- **THEN** every participant SHALL receive a `context` list where `context[-1]` corresponds to the triggering message

#### Scenario: context is never empty when on_message is called
- **WHEN** the dispatch shell calls `on_message`
- **THEN** `context` SHALL contain at least one item
