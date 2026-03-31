# Spec: echo-bot

## Purpose

Defines the `EchoBot` participant — a minimal bot that echoes back any message sent by another participant, while ignoring its own messages to avoid infinite loops.

## Requirements

### Requirement: EchoBot echoes messages from other participants
The `EchoBot` participant SHALL reply to any message whose sender is not the bot itself by returning a `ChatMessage` containing the same text as the original message. The reply's timestamp SHALL be set by the caller (dispatch shell), not by `EchoBot` itself.

#### Scenario: Human message is echoed
- **WHEN** a human participant posts a message with text "hello"
- **THEN** `EchoBot.on_message` SHALL return a `ChatMessage` with the same text "hello" and the bot's own name as sender

#### Scenario: EchoBot does not generate a timestamp
- **WHEN** `EchoBot.on_message` returns a reply
- **THEN** the reply's timestamp SHALL equal the timestamp of the incoming message (i.e. `EchoBot` does not call `datetime.now()`)

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
