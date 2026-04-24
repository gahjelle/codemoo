## MODIFIED Requirements

### Requirement: Mistral backend factory creates a working LLMBackend
The system SHALL provide a `create_mistral_backend(model: str) -> ToolLLMBackend` factory function in `llm/mistral.py` (not `llm/backend.py`) that reads `MISTRAL_API_KEY` from the environment and returns a `ToolLLMBackend` instance backed by the Mistral chat completion API. The model SHALL be passed explicitly by the caller (read from `config.models.backends["mistral"].model_name`). If `MISTRAL_API_KEY` is not set, it SHALL raise `BackendUnavailableError`.

#### Scenario: Factory raises BackendUnavailableError on missing API key
- **WHEN** `create_mistral_backend()` is called and `MISTRAL_API_KEY` is not set in the environment
- **THEN** it SHALL raise `BackendUnavailableError` with a message indicating the missing key

#### Scenario: Backend calls Mistral API with provided messages
- **WHEN** `complete(messages)` is called on a Mistral backend
- **THEN** it SHALL call the Mistral chat completion API with the given messages and the configured model, and return the response text

## ADDED Requirements

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
