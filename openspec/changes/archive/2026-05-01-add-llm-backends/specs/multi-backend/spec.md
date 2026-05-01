## ADDED Requirements

### Requirement: BackendConfig supports an optional base_url field
`BackendConfig` SHALL have an optional `base_url: str | None = None` field. When set, the factory SHALL pass it to the corresponding `create_*_backend()` function. Backends that do not use a custom URL (e.g. `anthropic`) SHALL ignore a `None` value. This enables OpenRouter, Google, and Ollama to have their URLs in TOML and lets the `openai` backend target Azure AI Foundry or other OpenAI-compatible endpoints.

#### Scenario: BackendConfig with base_url parses from TOML
- **WHEN** a `[models.backends.openrouter]` section includes `base_url = "https://openrouter.ai/api/v1"`
- **THEN** `BackendConfig.base_url` SHALL equal that string

#### Scenario: BackendConfig without base_url defaults to None
- **WHEN** a `[models.backends.openai]` section has only `model_name`
- **THEN** `BackendConfig.base_url` SHALL be `None`

### Requirement: openai, google, and ollama are registered backends
The `ModelBackend` literal type and the `_create()` dispatch in `factory.py` SHALL include `"openai"`, `"google"`, and `"ollama"`. Each maps to its respective `create_*_backend()` factory, which receives `model` and `base_url` from `BackendConfig`.

#### Scenario: openai backend dispatched correctly
- **WHEN** `config.models.backend = "openai"` and `OPENAI_API_KEY` is set
- **THEN** `resolve_backend()` SHALL return an OpenAI-backed `LLMBackend`

#### Scenario: google backend dispatched correctly
- **WHEN** `config.models.backend = "google"` and `GOOGLE_API_KEY` is set
- **THEN** `resolve_backend()` SHALL return a Google-backed `LLMBackend`

#### Scenario: ollama backend dispatched correctly
- **WHEN** `config.models.backend = "ollama"` and Ollama is running at the configured URL
- **THEN** `resolve_backend()` SHALL return an Ollama-backed `LLMBackend`

## MODIFIED Requirements

### Requirement: BackendInfo carries the active backend name and model
`resolve_backend` SHALL return a `BackendInfo(name: str, model: str)` frozen dataclass alongside the backend instance. `name` is the config key (`"mistral"`, `"anthropic"`, `"openrouter"`, `"openai"`, `"google"`, `"ollama"`); `model` is the model name string used for that backend.

#### Scenario: BackendInfo reflects the selected backend
- **WHEN** `resolve_backend` selects the `"anthropic"` backend with model `"claude-haiku-4-5-20251001"`
- **THEN** the returned `BackendInfo` SHALL have `name="anthropic"` and `model="claude-haiku-4-5-20251001"`

### Requirement: OpenRouter backend uses OPENROUTER_API_KEY and base_url from config
The system SHALL provide a `create_openrouter_backend(model: str, base_url: str)` factory in `llm/openrouter.py` that reads `OPENROUTER_API_KEY` from the environment and raises `BackendUnavailableError` if it is absent. The `base_url` parameter is required and SHALL be sourced from `BackendConfig.base_url` in `codemoo.toml`; there is no hardcoded fallback URL in code.

#### Scenario: OpenRouter backend raises BackendUnavailableError without key
- **WHEN** `create_openrouter_backend()` is called and `OPENROUTER_API_KEY` is not set
- **THEN** it SHALL raise `BackendUnavailableError`

#### Scenario: base_url from config is used
- **WHEN** `BackendConfig.base_url = "https://openrouter.ai/api/v1"` is set in TOML
- **THEN** the factory SHALL construct the client with that URL
