## MODIFIED Requirements

### Requirement: LLMBot responds using only the current message
When `on_message` is called, `LLMBot` SHALL send a single `Message(role="user", content=message.text)` to its backend and return the response as a `ChatMessage`. It SHALL ignore the `history` parameter entirely. The reply SHALL be constructed as `ChatMessage(sender=self.name, text=response)`, relying on the default factory for `timestamp`.

#### Scenario: LLMBot ignores history
- **WHEN** `on_message` is called with a non-empty `history`
- **THEN** the backend SHALL receive exactly one message containing only `message.text`

#### Scenario: LLMBot returns response as ChatMessage
- **WHEN** `on_message` is called with a human message
- **THEN** `LLMBot` SHALL return a `ChatMessage` with `sender == self.name` and `text` equal to the backend's response

## REMOVED Requirements

### Requirement: LLMBot does not respond to its own messages
**Reason**: The dispatch shell now guarantees that no participant receives its own messages.
**Migration**: Remove the `if message.sender == self.name: return None` guard from `LLMBot.on_message`.
