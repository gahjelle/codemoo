## ADDED Requirements

### Requirement: estimate_tokens returns an integer token count from a list of Messages
`src/codemoo/core/token_counter.py` SHALL expose `estimate_tokens(messages: list[Message]) -> int`. It SHALL use the `cl100k_base` tiktoken encoder, instantiated once at module level. It SHALL count tokens in both `message.content` and `message.tool_calls_json` for each message, treating `None` values as empty strings. The return value is the sum across all messages.

#### Scenario: Empty message list returns zero
- **WHEN** `estimate_tokens([])` is called
- **THEN** it SHALL return `0`

#### Scenario: Counts content tokens
- **WHEN** `estimate_tokens([Message(role="user", content="hello world")])` is called
- **THEN** it SHALL return the token count of `"hello world"` according to `cl100k_base`

#### Scenario: Counts tool_calls_json tokens in addition to content
- **WHEN** a message has both `content` and `tool_calls_json` set
- **THEN** tokens from both fields SHALL be summed in the result

#### Scenario: None content and None tool_calls_json treated as empty string
- **WHEN** `message.content` or `message.tool_calls_json` is `None`
- **THEN** no tokens SHALL be added for that field (equivalent to counting `""`)
