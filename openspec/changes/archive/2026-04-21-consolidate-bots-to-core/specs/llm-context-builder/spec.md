## ADDED Requirements

### Requirement: build_llm_context is a pure function that produces a Message list
The system SHALL provide a module-level function `build_llm_context(history, current, bot_name, human_name, max_messages) -> list[Message]` in `core/backend.py`. It SHALL be a pure function with no IO or async behaviour.

#### Scenario: Function returns a list of Message objects
- **WHEN** `build_llm_context` is called with a history and a current message
- **THEN** it SHALL return a `list[Message]` suitable for passing to an `LLMBackend.complete` call

### Requirement: build_llm_context filters history to relevant senders
Only messages from the human participant and the bot itself SHALL be included. Messages from any other participant SHALL be excluded.

#### Scenario: Messages from third parties are excluded
- **WHEN** history contains messages from a sender that is neither `human_name` nor `bot_name`
- **THEN** those messages SHALL NOT appear in the returned list

### Requirement: build_llm_context maps senders to LLM roles
Human messages SHALL be mapped to `Message(role="user", ...)` and bot messages to `Message(role="assistant", ...)`. The current message SHALL always be appended as a final `Message(role="user", ...)`.

#### Scenario: Bot history messages become assistant role
- **WHEN** a filtered history message has `sender == bot_name`
- **THEN** it SHALL appear in the output as `Message(role="assistant", content=message.text)`

#### Scenario: Human history messages become user role
- **WHEN** a filtered history message has `sender == human_name`
- **THEN** it SHALL appear in the output as `Message(role="user", content=message.text)`

#### Scenario: Current message is the final user turn
- **WHEN** `build_llm_context` is called
- **THEN** the last element of the returned list SHALL be `Message(role="user", content=current.text)`

### Requirement: build_llm_context clips filtered history to max_messages
Before appending the current message, the filtered history SHALL be clipped to the most recent `max_messages` entries.

#### Scenario: History exceeding max_messages is clipped
- **WHEN** the filtered history contains more than `max_messages` entries
- **THEN** only the most recent `max_messages` entries SHALL be included, followed by the current message

#### Scenario: History within limit is not clipped
- **WHEN** the filtered history contains `max_messages` or fewer entries
- **THEN** all filtered history entries SHALL be included
