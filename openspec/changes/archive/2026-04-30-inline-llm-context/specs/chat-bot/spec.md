## MODIFIED Requirements

### Requirement: ChatBot builds LLM context from history
When `on_message` is called, `ChatBot` SHALL build a `list[Message]` inline by mapping each message in `history` to a `Message` with `role="assistant"` if `m.sender == self.name`, otherwise `role="user"`. It SHALL then append `Message(role="user", content=message.text)` as the final element using list unpacking. The resulting list SHALL be passed to the backend. The reply SHALL be constructed as `ChatMessage(sender=self.name, text=response)`.

`ChatBot` SHALL NOT delegate context-building to `build_llm_context`. `ChatBot` SHALL NOT carry `human_name` or `max_messages` fields.

#### Scenario: Own history messages are mapped to assistant role
- **WHEN** `history` contains a message with `sender == self.name`
- **THEN** it SHALL be sent to the backend as `Message(role="assistant", content=m.text)`

#### Scenario: All other history messages are mapped to user role
- **WHEN** `history` contains a message with `sender != self.name`
- **THEN** it SHALL be sent to the backend as `Message(role="user", content=m.text)`

#### Scenario: Messages from third parties are included as user role
- **WHEN** `history` contains messages from a sender that is neither the human nor `self.name`
- **THEN** those messages SHALL appear in the list sent to the backend with `role="user"`

#### Scenario: Current message is the final user turn
- **WHEN** `on_message` is called
- **THEN** the last element of the list sent to the backend SHALL be `Message(role="user", content=message.text)`

#### Scenario: ChatBot constructs reply without explicit timestamp
- **WHEN** `ChatBot.on_message` returns a reply
- **THEN** the reply SHALL be a `ChatMessage` constructed with `sender` and `text` only

## REMOVED Requirements

### Requirement: ChatBot clips context to a configurable maximum message count
**Reason**: `max_messages` is removed from `ChatBot`. No clipping is applied.
**Migration**: No replacement. Introduce a dedicated context-management layer if needed.
