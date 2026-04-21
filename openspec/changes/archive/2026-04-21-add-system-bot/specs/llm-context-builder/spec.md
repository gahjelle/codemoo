## MODIFIED Requirements

### Requirement: build_llm_context is a pure function that produces a Message list
The system SHALL provide a module-level function `build_llm_context(history, current, bot_name, human_name, max_messages, system="") -> list[Message]` in `core/backend.py`. It SHALL be a pure function with no IO or async behaviour. The `system` parameter SHALL default to an empty string.

#### Scenario: Function returns a list of Message objects
- **WHEN** `build_llm_context` is called with a history and a current message
- **THEN** it SHALL return a `list[Message]` suitable for passing to an `LLMBackend.complete` call

#### Scenario: Function signature accepts optional system parameter
- **WHEN** `build_llm_context` is called without a `system` argument
- **THEN** it SHALL behave identically to the prior signature

### Requirement: build_llm_context prepends a system message when system is non-empty
When `system` is a non-empty string, `build_llm_context` SHALL prepend `Message(role="system", content=system)` as the first element of the returned list, before all history and the current message.

#### Scenario: System message is first when system is provided
- **WHEN** `build_llm_context` is called with a non-empty `system` string
- **THEN** the first element of the returned list SHALL be `Message(role="system", content=system)`

#### Scenario: No system message when system is empty
- **WHEN** `build_llm_context` is called with `system=""` (the default)
- **THEN** the returned list SHALL NOT contain any `Message` with `role="system"`
