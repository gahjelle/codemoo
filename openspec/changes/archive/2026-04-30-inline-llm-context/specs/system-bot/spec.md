## MODIFIED Requirements

### Requirement: SystemBot accepts a system prompt string
`SystemBot` SHALL accept an `instructions: str` field at construction. This string SHALL be prepended as `Message(role="system", content=self.instructions)` as the first element of the context list on every `on_message` call. `SystemBot` SHALL NOT delegate to `build_llm_context`. `SystemBot` SHALL NOT carry `human_name` or `max_messages` fields.

#### Scenario: System prompt is the first message in context
- **WHEN** `SystemBot.on_message` is called with any message
- **THEN** the first element of the list sent to the backend SHALL be `Message(role="system", content=self.instructions)`

### Requirement: SystemBot builds context inline from history
`SystemBot` SHALL build its `list[Message]` inline: `[Message(role="system", content=self.instructions), *[Message(role="assistant" if m.sender == self.name else "user", content=m.text) for m in history], Message(role="user", content=message.text)]`. Messages from third-party participants SHALL be included as `role="user"`.

#### Scenario: System message present alongside history
- **WHEN** `history` is non-empty
- **THEN** the list sent to the backend SHALL begin with the system message, followed by the mapped history, followed by the current message

#### Scenario: Messages from third parties are included as user role
- **WHEN** `history` contains messages from a sender that is neither the human nor `self.name`
- **THEN** those messages SHALL appear in the list sent to the backend with `role="user"`

#### Scenario: Current message is the final user turn
- **WHEN** `on_message` is called
- **THEN** the last element of the list sent to the backend SHALL be `Message(role="user", content=message.text)`

## REMOVED Requirements

### Requirement: SystemBot builds context using the same history rules as ChatBot
**Reason**: `build_llm_context` is removed. Context is built inline without filtering or clipping.
**Migration**: See "SystemBot builds context inline from history" above.
