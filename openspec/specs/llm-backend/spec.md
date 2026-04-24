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
The system SHALL define an `LLMBackend` structural protocol in `core/backend.py` with a single async method `complete(messages: list[Message]) -> str`. Any object implementing this interface SHALL be usable as a backend without explicit subclassing.

#### Scenario: Protocol is satisfied by any matching implementation
- **WHEN** an object exposes an async `complete(messages: list[Message]) -> str` method
- **THEN** it SHALL satisfy the `LLMBackend` protocol

### Requirement: Mistral backend factory creates a working LLMBackend
The system SHALL provide a `create_mistral_backend(model: str) -> LLMBackend` factory function in `llm/backend.py` that reads `MISTRAL_API_KEY` from the environment and returns an `LLMBackend` instance backed by the Mistral chat completion API. The default value for `model` SHALL be determined by reading `CODEMOO_MISTRAL_MODEL` from the environment; if that env var is not set, the default SHALL be `"mistral-small-latest"`.

#### Scenario: Factory raises on missing API key
- **WHEN** `create_mistral_backend` is called and `MISTRAL_API_KEY` is not set in the environment
- **THEN** it SHALL raise a `ValueError` with a message indicating the missing key

#### Scenario: Backend calls Mistral API with provided messages
- **WHEN** `complete(messages)` is called on a Mistral backend
- **THEN** it SHALL call the Mistral chat completion API with the given messages and the configured model, and return the response text

#### Scenario: CODEMOO_MISTRAL_MODEL overrides default model
- **WHEN** `CODEMOO_MISTRAL_MODEL` is set and `create_mistral_backend()` is called without an explicit `model` argument
- **THEN** the backend SHALL use the model name from `CODEMOO_MISTRAL_MODEL`
