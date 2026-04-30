# Spec: llm-completion

## Purpose

Defines the unified LLM completion interface that replaces separate `complete()` and `complete_step()` methods with a single `complete(messages, tools=None)` method supporting both text and tool operations.

## Requirements

### Requirement: Unified complete method signature
The system SHALL provide a unified `complete(messages, tools=None)` method in the `ToolLLMBackend` protocol that replaces both `complete()` and `complete_step()`. The method SHALL accept a `messages` parameter of type `list[Message]` and an optional `tools` parameter of type `list[ToolDef] | None`.

#### Scenario: Method accepts messages parameter
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL accept the messages parameter and process it

#### Scenario: Method accepts optional tools parameter
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL accept None for tools parameter
- **WHEN** `complete(messages, tools=[...])` is called
- **THEN** it SHALL accept a list of ToolDef instances

### Requirement: Unified return type str | ToolUse
The unified `complete()` method SHALL return `str | ToolUse`. It SHALL return `str` when no tools are provided or when the LLM returns a text response. It SHALL return `ToolUse` when tools are provided and the LLM requests a tool call.

#### Scenario: Returns str when no tools provided
- **WHEN** `complete(messages, tools=None)` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns str when tools provided but LLM returns text
- **WHEN** `complete(messages, tools=[...])` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns ToolUse when tools provided and LLM requests tool call
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests tool call
- **THEN** it SHALL return a `ToolUse` instance with tool name and arguments

### Requirement: Backward compatible calling pattern for simple completion
The unified method SHALL support the same calling pattern as the original `complete()` method for simple text completion.

#### Scenario: Simple completion works without tools parameter
- **WHEN** `complete(messages)` is called (without tools parameter)
- **THEN** it SHALL behave identically to the original `complete(messages)` method

#### Scenario: Simple completion works with explicit None tools
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL behave identically to the original `complete(messages)` method
