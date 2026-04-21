## MODIFIED Requirements

### Requirement: EchoBot echoes messages from other participants
The `EchoBot` participant SHALL reply to any received message by returning a `ChatMessage` containing the same text as the original message and the bot's own name as sender. The reply's timestamp SHALL be set automatically by `ChatMessage`'s default factory at construction time.

#### Scenario: Human message is echoed
- **WHEN** a human participant posts a message with text "hello"
- **THEN** `EchoBot.on_message` SHALL return a `ChatMessage` with the same text "hello" and the bot's own name as sender

#### Scenario: EchoBot constructs reply without explicit timestamp
- **WHEN** `EchoBot.on_message` returns a reply
- **THEN** the reply SHALL be a `ChatMessage` constructed with `sender` and `text` only, relying on the default factory for `timestamp`

## REMOVED Requirements

### Requirement: EchoBot does not echo its own messages
**Reason**: The dispatch shell now guarantees that no participant receives its own messages. Individual bots no longer need to guard against this.
**Migration**: Remove the `if message.sender == self.name: return None` guard from `EchoBot.on_message`.
