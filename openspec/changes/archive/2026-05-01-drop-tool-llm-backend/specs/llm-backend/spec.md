## REMOVED Requirements

### Requirement: ToolLLMBackend extends LLMBackend with tool support
**Reason**: `ToolLLMBackend` and `LLMBackend` have identical `complete()` signatures; the subprotocol expresses no additional constraint and was only a marker. `LLMBackend` is now the single protocol for all backends including those with tool support.
**Migration**: Replace `ToolLLMBackend` with `LLMBackend` everywhere it appears. No behavioral change is required.

## MODIFIED Requirements

### Requirement: resolve_backend is the canonical public entry point for backend creation
The `llm/factory.py` module SHALL export `resolve_backend(config) -> tuple[LLMBackend, BackendInfo]` as the canonical way to obtain a backend in frontend code. Direct calls to `create_mistral_backend` and similar factories SHALL be internal to the `llm` package.

#### Scenario: Frontends use resolve_backend, not create_mistral_backend
- **WHEN** `tui.py` or `cli.py` initializes the backend
- **THEN** it SHALL call `resolve_backend(config)` and SHALL NOT call `create_mistral_backend` directly

### Requirement: Mistral backend factory creates a working LLMBackend
The system SHALL provide a `create_mistral_backend(model: str) -> LLMBackend` factory function in `llm/mistral.py` that reads `MISTRAL_API_KEY` from the environment and returns an `LLMBackend` instance backed by the Mistral chat completion API. The model SHALL be passed explicitly by the caller. If `MISTRAL_API_KEY` is not set, it SHALL raise `BackendUnavailableError`.

#### Scenario: Factory raises BackendUnavailableError on missing API key
- **WHEN** `create_mistral_backend()` is called and `MISTRAL_API_KEY` is not set in the environment
- **THEN** it SHALL raise `BackendUnavailableError` with a message indicating the missing key

#### Scenario: Backend calls Mistral API with provided messages
- **WHEN** `complete(messages)` is called on a Mistral backend
- **THEN** it SHALL call the Mistral chat completion API with the given messages and the configured model, and return the response text
