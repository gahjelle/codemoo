## MODIFIED Requirements

### Requirement: LLMBot responds using only the current message
When `on_message` is called, `LLMBot` SHALL send a single `Message(role="user", content=context[-1].content.text)` to its backend and return the response as a `ContextItem`. It SHALL ignore all items in `context` except the last one. `context[-1]` is guaranteed to be the triggering message by the dispatch shell precondition.

#### Scenario: LLMBot ignores all context except the last item
- **WHEN** `on_message` is called with a context containing multiple items
- **THEN** the backend SHALL receive exactly one message containing only `context[-1].content.text`

#### Scenario: LLMBot returns response as AssistantMessageContent
- **WHEN** `on_message` is called
- **THEN** `LLMBot` SHALL return a list containing one `ContextItem` whose content is `AssistantMessageContent` with `text` equal to the backend's response
