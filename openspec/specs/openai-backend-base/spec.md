# Spec: openai-backend-base

## Purpose

Defines the `OpenAILikeBackend` base class that provides common implementation for OpenAI-compatible LLM backends (Mistral, OpenRouter, and future providers using the OpenAI API format).

## Requirements

### Requirement: OpenAILikeBackend base class
The system SHALL provide an `OpenAILikeBackend` base class in an appropriate module that implements the unified `complete(messages, tools=None)` method using the OpenAI-compatible API format.

#### Scenario: Base class implements ToolLLMBackend protocol
- **WHEN** `OpenAILikeBackend` is inspected
- **THEN** it SHALL implement the `ToolLLMBackend` protocol with the unified `complete()` method

#### Scenario: Base class provides common serialization
- **WHEN** `OpenAILikeBackend._serialize()` is called
- **THEN** it SHALL convert Message objects to OpenAI-compatible dict format

### Requirement: Common tool schema conversion
The base class SHALL provide a `_tool_schema()` method that converts `ToolDef` instances to the OpenAI function-calling wire format.

#### Scenario: ToolDef converted to OpenAI format
- **WHEN** `_tool_schema(tool_def)` is called
- **THEN** it SHALL return a dict in OpenAI function-calling format with name, description, and parameters

### Requirement: Unified complete method implementation
The base class SHALL implement the unified `complete(messages, tools=None)` method that handles both text completion and tool calling through the OpenAI-compatible API.

#### Scenario: Text completion when no tools provided
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL call the API without tools and return the response text as `str`

#### Scenario: Tool calling when tools provided
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests tool
- **THEN** it SHALL return a `ToolUse` instance with tool name and arguments

#### Scenario: Text response when tools provided but LLM returns text
- **WHEN** `complete(messages, tools=[...])` is called and LLM returns text
- **THEN** it SHALL return the text as `str`

### Requirement: Concrete backends inherit from base class
MistralBackend and OpenRouterBackend SHALL inherit from `OpenAILikeBackend` and provide only the minimal necessary overrides.

#### Scenario: MistralBackend inherits from base class
- **WHEN** `MistralBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`

#### Scenario: OpenRouterBackend inherits from base class
- **WHEN** `OpenRouterBackend` is inspected
- **THEN** it SHALL be a subclass of `OpenAILikeBackend`
