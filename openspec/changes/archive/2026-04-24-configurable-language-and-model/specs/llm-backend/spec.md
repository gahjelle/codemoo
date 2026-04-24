## MODIFIED Requirements

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
