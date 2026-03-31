## MODIFIED Requirements

### Requirement: EchoBot echoes messages from other participants
The `EchoBot` participant SHALL reply to any message whose sender is not the bot itself by returning a `ChatMessage` containing the same text as the original message. The reply's timestamp SHALL be set by the caller (dispatch shell), not by `EchoBot` itself.

#### Scenario: Human message is echoed
- **WHEN** a human participant posts a message with text "hello"
- **THEN** `EchoBot.on_message` SHALL return a `ChatMessage` with the same text "hello" and the bot's own name as sender

#### Scenario: EchoBot does not generate a timestamp
- **WHEN** `EchoBot.on_message` returns a reply
- **THEN** the reply's timestamp SHALL equal the timestamp of the incoming message (i.e. `EchoBot` does not call `datetime.now()`)
