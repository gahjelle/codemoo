# Spec: llm-backend

## Purpose

Defines the `Message` value type and `Role` type alias, the `LLMBackend` structural protocol, and concrete backend factories (starting with Mistral) that connect the chat system to external language model APIs.

## MODIFIED Requirements

### Requirement: LLMBackend protocol defines a single async complete method
The system SHALL define an `LLMBackend` structural protocol in `core/backend.py` with a single async method `complete(messages: list[Message], tools: list[ToolDef] | None = None) -> str | ToolUse`. Any object implementing this interface SHALL be usable as a backend without explicit subclassing. This replaces the previous dual-method approach with `complete()` and `complete_step()`.

#### Scenario: Protocol is satisfied by any matching implementation
- **WHEN** an object exposes an async `complete(messages: list[Message], tools: list[ToolDef] | None = None) -> str | ToolUse` method
- **THEN** it SHALL satisfy the `LLMBackend` protocol

#### Scenario: Unified method handles both text and tool completion
- **WHEN** `complete(messages)` is called without tools parameter
- **THEN** it SHALL behave as text-only completion
- **WHEN** `complete(messages, tools=[...])` is called
- **THEN** it SHALL handle tool-aware completion and return either `str` or `ToolUse`

## ADDED Requirements

### Requirement: ToolLLMBackend extends LLMBackend with tool support
The system SHALL define a `ToolLLMBackend` protocol that extends `LLMBackend` to indicate backends that support tool calling. This protocol SHALL be satisfied by any backend that implements the unified `complete()` method with proper tool handling.

#### Scenario: ToolLLMBackend is satisfied by complete method implementation
- **WHEN** a backend implements `complete(messages, tools=None)` with tool support
- **THEN** it SHALL satisfy the `ToolLLMBackend` protocol

### Requirement: TextResponse class is removed
The system SHALL remove the `TextResponse` class from `core/backend.py` since the unified method returns `str` directly for text responses.

#### Scenario: TextResponse is no longer used
- **WHEN** backend code is inspected
- **THEN** it SHALL NOT import or use `TextResponse`

## REMOVED Requirements

### Requirement: LLMBackend exposes complete_step for structured single-turn responses
**Reason**: Replaced by unified `complete()` method with optional tools parameter
**Migration**: Use `complete(messages, tools=[...])` instead of `complete_step(messages, tools)`
