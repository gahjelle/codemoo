## MODIFIED Requirements

### Requirement: ChatBot builds LLM context from filtered history
When `on_message` is called, `ChatBot` SHALL delegate context-building to `build_llm_context` (from `core/backend.py`), passing `history`, the current message, `self.name`, `human_name`, and `max_messages`. The resulting `list[Message]` SHALL be passed to the backend.

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
