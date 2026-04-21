## MODIFIED Requirements

### Requirement: ChatBot builds LLM context from filtered history
When `on_message` is called, `ChatBot` SHALL delegate context-building to `build_llm_context`, passing `history`, the current message, `self.name`, `human_name`, and `max_messages`. The resulting `list[Message]` SHALL be passed to the backend. The reply SHALL be constructed as `ChatMessage(sender=self.name, text=response)`, relying on the default factory for `timestamp`.

#### Scenario: Messages from other bots are excluded from context
- **WHEN** `history` contains messages from a third participant (neither human nor self)
- **THEN** those messages SHALL NOT appear in the list sent to the backend

#### Scenario: Own history messages are mapped to assistant role
- **WHEN** `history` contains a message with `sender == self.name`
- **THEN** it SHALL be sent to the backend as `Message(role="assistant", ...)`

#### Scenario: Human history messages are mapped to user role
- **WHEN** `history` contains a message with `sender == human_name`
- **THEN** it SHALL be sent to the backend as `Message(role="user", ...)`

#### Scenario: Current message is appended as final user turn
- **WHEN** `on_message` is called
- **THEN** the final message in the list sent to the backend SHALL be `Message(role="user", content=message.text)`

#### Scenario: ChatBot constructs reply without explicit timestamp
- **WHEN** `ChatBot.on_message` returns a reply
- **THEN** the reply SHALL be a `ChatMessage` constructed with `sender` and `text` only

## REMOVED Requirements

### Requirement: ChatBot does not respond to its own messages
**Reason**: The dispatch shell now guarantees that no participant receives its own messages.
**Migration**: Remove the `if message.sender == self.name: return None` guard from `ChatBot.on_message`.
