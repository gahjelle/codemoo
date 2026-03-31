## ADDED Requirements

### Requirement: EchoBot echoes messages from other participants
The `EchoBot` participant SHALL reply to any message whose sender is not the bot itself by returning a `ChatMessage` containing the same text as the original message.

#### Scenario: Human message is echoed
- **WHEN** a human participant posts a message with text "hello"
- **THEN** `EchoBot.on_message` SHALL return a `ChatMessage` with the same text "hello" and the bot's own name as sender

### Requirement: EchoBot does not echo its own messages
The `EchoBot` participant SHALL return `None` when `on_message` is called with a message whose sender matches the bot's own name.

#### Scenario: Own message is ignored
- **WHEN** `on_message` is called with a `ChatMessage` whose sender equals `EchoBot.name`
- **THEN** `EchoBot.on_message` SHALL return `None`

### Requirement: EchoBot has a fixed display name
The `EchoBot` SHALL expose a stable `name` property used as the sender field in its replies.

#### Scenario: Name is accessible
- **WHEN** `EchoBot.name` is accessed
- **THEN** it SHALL return a non-empty string identifying the bot
