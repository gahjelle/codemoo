## MODIFIED Requirements

### Requirement: EchoBot echoes messages from other participants
The `EchoBot` participant SHALL reply to any received message by returning a `ContextItem` containing the same text as `context[-1].content.text` and the bot's own name as sender. `context[-1]` is guaranteed to be the triggering message by the dispatch shell precondition.

#### Scenario: Human message is echoed
- **WHEN** a human participant posts a message with text "hello"
- **THEN** `EchoBot.on_message` SHALL return a `ContextItem` whose `AssistantMessageContent.text` equals "hello"

#### Scenario: EchoBot reads triggering text from context
- **WHEN** `EchoBot.on_message` is called with a context whose last item has text "hello"
- **THEN** the returned item's text SHALL equal "hello", sourced from `context[-1].content.text`
