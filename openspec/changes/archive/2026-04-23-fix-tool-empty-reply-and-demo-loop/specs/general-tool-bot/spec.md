## MODIFIED Requirements

### Requirement: GeneralToolBot implements the single-round-trip tool-call loop
`GeneralToolBot` SHALL be a concrete dataclass that implements `on_message`. It SHALL call `backend.complete_step(context, self.tools)`, and if the result is a `ToolUse`, invoke the matched tool's `fn`, append the result to context as a `tool`-role message, and call `backend.complete` to get the final reply. If the result is a `TextResponse`, it SHALL use that text directly. If the follow-up `backend.complete` returns an empty string, `GeneralToolBot` SHALL substitute the fallback string `"(tool executed, process interrupted)"` so that an empty-text `ChatMessage` is never stored in history.

#### Scenario: Text response path — no second complete call
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `GeneralToolBot.on_message` SHALL return a `ChatMessage` with that text and SHALL NOT call `backend.complete`

#### Scenario: Tool-use path — tool invoked and result fed back
- **WHEN** `backend.complete_step` returns a `ToolUse` naming a registered tool
- **THEN** `GeneralToolBot` SHALL invoke the tool's `fn`, append the output as a `tool`-role message, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Tool-use path — empty follow-up reply replaced with fallback
- **WHEN** `backend.complete_step` returns a `ToolUse` and the subsequent `backend.complete` call returns an empty string
- **THEN** `GeneralToolBot.on_message` SHALL return a `ChatMessage` with text `"(tool executed, process interrupted)"` and SHALL NOT store an empty string in the returned message

#### Scenario: Reply uses bot name as sender
- **WHEN** `GeneralToolBot.on_message` returns a reply
- **THEN** `reply.sender` SHALL equal `self.name`
