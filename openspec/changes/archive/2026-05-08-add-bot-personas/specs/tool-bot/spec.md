## MODIFIED Requirements

### Requirement: ToolBot uses a lightweight system prompt
`ToolBot` SHALL include a default `instructions: str` field (re-declared in `ToolBot` with `_INSTRUCTIONS` as default) that follows the four-part form: identity as "a coding assistant", a capability sentence explaining tools are available, a behavior trigger encouraging their use when relevant, and the credo "A tool call now beats an assumption later." as the final sentence.

#### Scenario: Default system prompt is forwarded to context builder
- **WHEN** `ToolBot.on_message` is called and no custom `instructions` is provided
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that follows the four-part prompt form and ends with the Telo credo
