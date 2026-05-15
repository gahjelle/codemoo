## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, an `is_human: bool` class variable, and an async `on_message(context: list[ContextItem]) -> list[ContextItem]` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

#### Scenario: Bot with a text reply ends its list with AssistantMessageContent
- **WHEN** a bot participant returns from `on_message`
- **THEN** if it has a text reply, the last item in the returned list SHALL have `content` of type `AssistantMessageContent`

#### Scenario: Bot with no reply returns an empty list
- **WHEN** a participant has no reply (e.g. `HumanParticipant`, `ErrorBot`)
- **THEN** `on_message` SHALL return `[]`

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
