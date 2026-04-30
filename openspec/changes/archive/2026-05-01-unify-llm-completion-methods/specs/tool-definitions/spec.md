# Spec: tool-definitions

## Purpose

Defines the `ToolDef` abstraction, the `reverse_string` built-in tool, and the unified `complete` backend method that enables both simple text completion and structured single-turn LLM responses with tool-calling support.

## MODIFIED Requirements

### Requirement: LLMBackend exposes complete for unified text and tool completion
`LLMBackend` SHALL expose a unified `complete(messages, tools=None)` method that replaces both `complete()` and `complete_step()`. It SHALL send one request to the LLM with the provided tools list and return either a `str` if the LLM replied with text, or a `ToolUse(name: str, arguments: dict)` if the LLM requested a tool call. It SHALL NOT invoke the tool function or re-submit to the LLM — that is the caller's responsibility.

#### Scenario: LLM replies with text — str is returned
- **WHEN** the LLM responds with a plain text message (no tool call)
- **THEN** `complete` SHALL return a `str` with the response text

#### Scenario: LLM requests a tool call — ToolUse is returned
- **WHEN** the LLM responds with a tool-call request
- **THEN** `complete` SHALL return a `ToolUse` with the tool name and argument dict, without invoking the tool

#### Scenario: Text completion when no tools provided
- **WHEN** `complete(messages)` is called without tools parameter
- **THEN** it SHALL behave as text-only completion and return `str`

#### Scenario: Tool calling when tools provided
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests tool
- **THEN** it SHALL return a `ToolUse` instance

## REMOVED Requirements

### Requirement: LLMBackend exposes complete_step for structured single-turn responses
**Reason**: Replaced by unified `complete()` method with optional tools parameter
**Migration**: Use `complete(messages, tools=[...])` instead of `complete_step(messages, tools)`
