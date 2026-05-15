## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, an `is_human: bool` class variable, and an async `on_message(message: ChatMessage, context: list[ContextItem]) -> list[ContextItem]` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

#### Scenario: Bot with a text reply ends its list with AssistantMessageContent
- **WHEN** a bot participant returns from `on_message`
- **THEN** if it has a text reply, the last item in the returned list SHALL have `content` of type `AssistantMessageContent`

#### Scenario: Bot with no reply returns an empty list
- **WHEN** a participant has no reply (e.g. `HumanParticipant`, `ErrorBot`)
- **THEN** `on_message` SHALL return `[]`

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
