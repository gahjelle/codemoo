## ADDED Requirements

### Requirement: SystemBot satisfies the ChatParticipant protocol
`SystemBot` SHALL implement the `ChatParticipant` protocol: it SHALL expose `name: str`, `emoji: str`, and `is_human: bool` attributes, and an async `on_message(message, history) -> ChatMessage | None` method. `is_human` SHALL always return `False`.

#### Scenario: SystemBot.is_human returns False
- **WHEN** `SystemBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: SystemBot accepts a system prompt string
`SystemBot` SHALL accept a `system: str` field at construction. This string SHALL be passed to `build_llm_context` on every `on_message` call.

#### Scenario: System prompt is forwarded to context builder
- **WHEN** `SystemBot.on_message` is called with any message
- **THEN** `build_llm_context` SHALL be called with the `system` field value as its `system` argument

### Requirement: SystemBot builds context using the same history rules as ChatBot
`SystemBot` SHALL delegate to `build_llm_context` with `history`, the current message, `self.name`, `human_name`, and `max_messages`, exactly as `ChatBot` does, but also passing `system`.

#### Scenario: Bot messages from other participants are excluded
- **WHEN** `history` contains messages from a third participant (neither human nor self)
- **THEN** those messages SHALL NOT appear in the list sent to the backend

#### Scenario: Context is clipped to max_messages
- **WHEN** filtered history exceeds `max_messages`
- **THEN** only the most recent `max_messages` entries SHALL be included, plus the current message

### Requirement: SystemBot constructs its reply from the backend response
The response from the backend SHALL be wrapped in a `ChatMessage(sender=self.name, text=response)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `SystemBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
