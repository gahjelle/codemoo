## ADDED Requirements

### Requirement: LLMBot satisfies the ChatParticipant protocol
`LLMBot` SHALL implement the `ChatParticipant` protocol: it SHALL expose `name: str`, `emoji: str`, and `is_human: bool` properties, and an async `on_message(message, history) -> ChatMessage | None` method. `is_human` SHALL always return `False`.

#### Scenario: LLMBot.is_human returns False
- **WHEN** `LLMBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: LLMBot responds using only the current message
When `on_message` is called, `LLMBot` SHALL send a single `LLMMessage(role="user", content=message.text)` to its backend and return the response as a `ChatMessage`. It SHALL ignore the `history` parameter entirely.

#### Scenario: LLMBot ignores history
- **WHEN** `on_message` is called with a non-empty `history`
- **THEN** the backend SHALL receive exactly one message containing only `message.text`

#### Scenario: LLMBot returns response as ChatMessage
- **WHEN** `on_message` is called with a human message
- **THEN** `LLMBot` SHALL return a `ChatMessage` with `sender == self.name` and `text` equal to the backend's response

### Requirement: LLMBot does not respond to its own messages
If the incoming message's sender matches `LLMBot.name`, `on_message` SHALL return `None` without calling the backend.

#### Scenario: LLMBot skips own messages
- **WHEN** `on_message` is called with a message whose sender equals `LLMBot.name`
- **THEN** it SHALL return `None` and the backend SHALL NOT be called
