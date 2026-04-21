## ADDED Requirements

### Requirement: LLMMessage is an immutable value type with role and content
The system SHALL provide an `LLMMessage` dataclass with a `role` field typed as `Literal["user", "assistant", "system"]` and a `content: str` field. It SHALL be frozen (immutable after construction).

#### Scenario: LLMMessage fields are accessible and immutable
- **WHEN** an `LLMMessage` is created with a role and content
- **THEN** those fields SHALL be readable and SHALL NOT be modifiable after construction

### Requirement: LLMBackend protocol defines a single async complete method
The system SHALL define an `LLMBackend` structural protocol with a single async method `complete(messages: list[LLMMessage]) -> str`. Any object implementing this interface SHALL be usable as a backend without explicit subclassing.

#### Scenario: Protocol is satisfied by any matching implementation
- **WHEN** an object exposes an async `complete(messages: list[LLMMessage]) -> str` method
- **THEN** it SHALL satisfy the `LLMBackend` protocol

### Requirement: Mistral backend factory creates a working LLMBackend
The system SHALL provide a `create_mistral_backend(model: str) -> LLMBackend` factory function that reads `MISTRAL_API_KEY` from the environment and returns an `LLMBackend` instance backed by the Mistral chat completion API.

#### Scenario: Factory raises on missing API key
- **WHEN** `create_mistral_backend` is called and `MISTRAL_API_KEY` is not set in the environment
- **THEN** it SHALL raise a `ValueError` with a message indicating the missing key

#### Scenario: Backend calls Mistral API with provided messages
- **WHEN** `complete(messages)` is called on a Mistral backend
- **THEN** it SHALL call the Mistral chat completion API with the given messages and the configured model, and return the response text
