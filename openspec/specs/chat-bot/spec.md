# Spec: chat-bot

## Purpose

Defines `ChatBot`, a context-aware chat participant that builds a filtered LLM conversation history from prior messages, enabling multi-turn dialogue with an `LLMBackend`.

## Requirements

### Requirement: ChatBot satisfies the ChatParticipant protocol
`ChatBot` SHALL implement the `ChatParticipant` protocol: it SHALL expose `name: str`, `emoji: str`, and `is_human: bool` attributes, and an async `on_message(message, history) -> ChatMessage | None` method. `is_human` SHALL always return `False`.

#### Scenario: ChatBot.is_human returns False
- **WHEN** `ChatBot.is_human` is accessed
- **THEN** it SHALL return `False`

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

### Requirement: ChatBot clips context to a configurable maximum message count
`ChatBot` SHALL accept a `max_messages: int` parameter (default: 20). Before calling the backend, it SHALL retain only the most recent `max_messages` messages from the filtered history, then append the current message.

#### Scenario: Context is clipped when history exceeds max_messages
- **WHEN** the filtered history contains more than `max_messages` entries
- **THEN** only the most recent `max_messages` entries SHALL be included, plus the current message

#### Scenario: Context is not clipped when history is within limit
- **WHEN** the filtered history contains `max_messages` or fewer entries
- **THEN** all filtered history entries SHALL be included

### Requirement: ChatBot does not respond to its own messages
If the incoming message's sender matches `ChatBot.name`, `on_message` SHALL return `None` without calling the backend.

#### Scenario: ChatBot skips own messages
- **WHEN** `on_message` is called with a message whose sender equals `ChatBot.name`
- **THEN** it SHALL return `None` and the backend SHALL NOT be called
