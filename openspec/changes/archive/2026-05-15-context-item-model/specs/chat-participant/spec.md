## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, is_human, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, an `is_human: bool` attribute, and an async `on_message(message: ChatMessage, context: list[ContextItem]) -> tuple[ChatMessage | None, list[ContextItem]]` method where the returned list contains only the new items produced this turn
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

---

### Requirement: Participant replies are posted to the chat
When a participant's `on_message` returns a tuple whose first element is a `ChatMessage`, the system SHALL post that reply to the chat and propagate it to all participants. The second element of the tuple is the list of new `ContextItem`s produced this turn; the application SHALL append these to its authoritative context. If `on_message` raises an exception, the dispatch loop SHALL catch it, yield an error message via `ErrorBot`, and continue processing remaining participants.

#### Scenario: Non-None reply is appended to the log
- **WHEN** a participant returns `(ChatMessage(...), new_items)` from `on_message`
- **THEN** the `ChatMessage` SHALL appear in the chat log and trigger another dispatch round
- **THEN** `new_items` SHALL be appended to the application's authoritative context list

#### Scenario: None reply produces no chat output but may still contribute context items
- **WHEN** a participant returns `(None, new_items)` from `on_message`
- **THEN** no additional chat message SHALL be posted
- **THEN** `new_items` SHALL be appended to the application's authoritative context list

#### Scenario: Exception does not crash the dispatch loop
- **WHEN** a participant's `on_message` raises an exception
- **THEN** the dispatch loop SHALL catch the exception, yield an `ErrorBot` error message, and continue with the remaining participants in the current dispatch round

---

### Requirement: Dispatch shell owns and passes list[ContextItem] to participants
The chat application SHALL own the authoritative `list[ContextItem]` for the session. On each dispatch, it SHALL pass the current context to `on_message` as a read-only input and append the returned new items to its context after the call returns. Only the application (via user-driven UI operations) SHALL modify existing context items; bots SHALL only append. The context SHALL start as an empty list at session start and SHALL be reset to an empty list on bot restart.

#### Scenario: Application records user message before dispatching
- **WHEN** the user submits a message
- **THEN** the application SHALL append a `ContextItem(UserMessageContent)` to its context before calling `on_message` on any participant

#### Scenario: Context starts empty at session start
- **WHEN** a new chat session begins
- **THEN** the initial context passed to the first `on_message` call SHALL contain only the user's first message as a `UserMessageContent` item

#### Scenario: Context accumulates across turns
- **WHEN** a participant returns an updated context from `on_message`
- **THEN** the next `on_message` call on any participant SHALL receive that updated context

#### Scenario: Context resets on restart
- **WHEN** a bot restart is triggered
- **THEN** the application's context SHALL be reset to an empty list

## REMOVED Requirements

### Requirement: Dispatch shell tracks and injects conversation history
**Reason:** Replaced by `list[ContextItem]` ownership in the dispatch shell. `list[ChatMessage]` history is no longer passed to participants; context items carry the full conversation record in a richer form.
**Migration:** Bots that previously read `history: list[ChatMessage]` to reconstruct LLM context SHALL instead call `build_context(context)` on the received `list[ContextItem]`.
