# Spec: agent-bot

## Purpose

TBD — defines AgentBot, a bot participant that implements an agentic loop, repeatedly calling the backend with tool use until a final text response is produced.

## Requirements

### Requirement: AgentBot loops tool calls until a TextResponse is returned
`AgentBot` SHALL implement `on_message` with an agentic loop: it SHALL call `backend.complete_step(context, self.tools)` repeatedly. On each `ToolUse` result it SHALL invoke the matched tool's `fn`, append the assistant's tool-use message and the `tool`-role result to the running context, then call `complete_step` again. The loop SHALL terminate when `complete_step` returns a `TextResponse`, and `on_message` SHALL return a `ChatMessage` with that text.

#### Scenario: Single tool call then text response
- **WHEN** `backend.complete_step` returns a `ToolUse` on the first call and a `TextResponse` on the second call
- **THEN** `AgentBot.on_message` SHALL invoke the tool once, feed its output back, and return a `ChatMessage` with the final text

#### Scenario: Multiple tool calls before text response
- **WHEN** `backend.complete_step` returns `ToolUse` on the first two calls and a `TextResponse` on the third
- **THEN** `AgentBot.on_message` SHALL invoke each tool in sequence, accumulate all tool outputs in context, and return a `ChatMessage` with the final text

#### Scenario: Immediate text response — no tool call
- **WHEN** `backend.complete_step` returns a `TextResponse` on the first call
- **THEN** `AgentBot.on_message` SHALL return a `ChatMessage` with that text and SHALL NOT invoke any tool

#### Scenario: Reply uses bot name as sender
- **WHEN** `AgentBot.on_message` returns a reply
- **THEN** `reply.sender` SHALL equal `self.name`

### Requirement: AgentBot satisfies the ChatParticipant protocol
`AgentBot` SHALL expose `name: str`, `emoji: str`, and `is_human: ClassVar[bool]` attributes. `is_human` SHALL always be `False`.

#### Scenario: is_human is False
- **WHEN** `is_human` is accessed on an `AgentBot` instance
- **THEN** it SHALL return `False`
