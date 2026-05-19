## MODIFIED Requirements

### Requirement: AgentBot loops tool calls until the LLM returns plain text
`AgentBot` SHALL implement `on_message` with an agentic loop. On each iteration it
SHALL call `self.llm.complete(messages, self.tools)`. When `complete` returns a
`list[ToolUse]`, `AgentBot` SHALL dispatch **all** tool calls in the list before
calling `complete` again — using a sequential `for`-loop over the list, invoking
`dispatch_tool` for each. After dispatching all calls, it SHALL append a single
combined assistant message (produced by `merge_tool_uses`) followed by one
`role="tool"` result message per call to the running context, then call `complete`
again. The loop SHALL terminate when `complete` returns a `str`, at which point
`on_message` SHALL return the accumulated `list[ContextItem]` for that turn.

#### Scenario: Single tool call then text response
- **WHEN** `complete` returns `[ToolUse]` on the first call and `str` on the second
- **THEN** `AgentBot.on_message` SHALL invoke the tool once, append the combined assistant message and one tool result, then return the final text as a `ContextItem`

#### Scenario: Multiple tool calls in one LLM response
- **WHEN** `complete` returns `[ToolUse, ToolUse]` on the first call and `str` on the second
- **THEN** `AgentBot.on_message` SHALL invoke both tools (sequentially), append one combined assistant message and two tool-result messages, then call `complete` once more before returning

#### Scenario: Multiple LLM rounds each with multiple tool calls
- **WHEN** `complete` returns `[ToolUse, ToolUse]` on the first call, `[ToolUse]` on the second, and `str` on the third
- **THEN** `AgentBot.on_message` SHALL invoke two tools in round one, one tool in round two, and return the final text — three `complete` calls total

#### Scenario: Immediate text response — no tool call
- **WHEN** `complete` returns `str` on the first call
- **THEN** `AgentBot.on_message` SHALL return a `ContextItem` with that text and SHALL NOT invoke any tool
