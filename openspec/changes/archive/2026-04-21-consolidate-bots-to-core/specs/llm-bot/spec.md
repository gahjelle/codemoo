## MODIFIED Requirements

### Requirement: LLMBot responds using only the current message
When `on_message` is called, `LLMBot` SHALL send a single `Message(role="user", content=message.text)` to its backend and return the response as a `ChatMessage`. It SHALL ignore the `history` parameter entirely.

#### Scenario: LLMBot ignores history
- **WHEN** `on_message` is called with a non-empty `history`
- **THEN** the backend SHALL receive exactly one message containing only `message.text`

#### Scenario: LLMBot returns response as ChatMessage
- **WHEN** `on_message` is called with a human message
- **THEN** `LLMBot` SHALL return a `ChatMessage` with `sender == self.name` and `text` equal to the backend's response
