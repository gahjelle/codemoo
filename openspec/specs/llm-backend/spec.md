# Spec: llm-backend

## Purpose

Defines the `Message` value type and `Role` type alias, the `LLMBackend` structural protocol, and concrete backend factories (starting with Mistral) that connect the chat system to external language model APIs.

## Requirements

### Requirement: Message is an immutable value type with role and content
The system SHALL provide a `Message` dataclass with a `role` field typed as `Role` (a `Literal["user", "assistant", "system"]` type alias) and a `content: str` field. It SHALL be frozen (immutable after construction). Both types SHALL live in `core/backend.py`.

#### Scenario: Message fields are accessible and immutable
- **WHEN** a `Message` is created with a role and content
- **THEN** those fields SHALL be readable and SHALL NOT be modifiable after construction

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

### Requirement: Mistral backend factory creates a working LLMBackend
The system SHALL provide a `create_mistral_backend(model: str) -> ToolLLMBackend` factory function in `llm/mistral.py` (not `llm/backend.py`) that reads `MISTRAL_API_KEY` from the environment and returns a `ToolLLMBackend` instance backed by the Mistral chat completion API. The model SHALL be passed explicitly by the caller (read from `config.models.backends["mistral"].model_name`). If `MISTRAL_API_KEY` is not set, it SHALL raise `BackendUnavailableError`.

#### Scenario: Factory raises BackendUnavailableError on missing API key
- **WHEN** `create_mistral_backend()` is called and `MISTRAL_API_KEY` is not set in the environment
- **THEN** it SHALL raise `BackendUnavailableError` with a message indicating the missing key

#### Scenario: Backend calls Mistral API with provided messages
- **WHEN** `complete(messages)` is called on a Mistral backend
- **THEN** it SHALL call the Mistral chat completion API with the given messages and the configured model, and return the response text

### Requirement: resolve_backend is the canonical public entry point for backend creation
The `llm/factory.py` module SHALL export `resolve_backend(config) -> tuple[ToolLLMBackend, BackendInfo]` as the canonical way to obtain a backend in frontend code. Direct calls to `create_mistral_backend` and similar factories SHALL be internal to the `llm` package.

#### Scenario: Frontends use resolve_backend, not create_mistral_backend
- **WHEN** `tui.py` or `cli.py` initializes the backend
- **THEN** it SHALL call `resolve_backend(config)` and SHALL NOT call `create_mistral_backend` directly

### Requirement: ModelBackend config type includes anthropic and openrouter
The `ModelBackend` type alias in `config/schema.py` SHALL be `Literal["mistral", "anthropic", "openrouter"]`.

#### Scenario: Config validation accepts all three backend names
- **WHEN** `config.models.backend` is set to `"anthropic"` or `"openrouter"`
- **THEN** config validation SHALL succeed without error
