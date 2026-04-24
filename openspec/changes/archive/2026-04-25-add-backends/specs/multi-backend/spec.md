## ADDED Requirements

### Requirement: resolve_backend selects the configured primary backend at startup
The system SHALL provide a `resolve_backend(config)` factory function in `llm/factory.py` that reads `config.models.backend` and attempts to create that backend. On success it SHALL return a `tuple[ToolLLMBackend, BackendInfo]`. It SHALL NOT catch network errors — only `BackendUnavailableError`.

#### Scenario: Primary backend is available
- **WHEN** `resolve_backend(config)` is called and `config.models.backend` is `"mistral"` with `MISTRAL_API_KEY` set
- **THEN** it SHALL return a `(ToolLLMBackend, BackendInfo(name="mistral", model=...))` tuple

### Requirement: resolve_backend falls back through config.models.fallbacks on unavailability
If the primary backend raises `BackendUnavailableError`, `resolve_backend` SHALL try each entry in `config.models.fallbacks` in order, stopping at the first that succeeds.

#### Scenario: Primary unavailable, first fallback used
- **WHEN** the primary backend raises `BackendUnavailableError` and the first fallback backend is available
- **THEN** `resolve_backend` SHALL return the first fallback backend and its `BackendInfo`

#### Scenario: All candidates unavailable
- **WHEN** the primary and all fallback backends raise `BackendUnavailableError`
- **THEN** `resolve_backend` SHALL raise an exception describing all attempted backends

### Requirement: BackendUnavailableError signals a missing API key
Each `create_*_backend()` factory SHALL raise `BackendUnavailableError` when its required API key environment variable is not set. This error SHALL be distinct from runtime errors so the fallback loop catches only the expected failure mode.

#### Scenario: Missing API key raises BackendUnavailableError
- **WHEN** `create_mistral_backend()` is called and `MISTRAL_API_KEY` is absent
- **THEN** it SHALL raise `BackendUnavailableError` (not a bare `ValueError`)

#### Scenario: Network errors are not caught
- **WHEN** the backend raises any exception other than `BackendUnavailableError` during a completion call
- **THEN** that exception SHALL propagate to the caller unchanged

### Requirement: BackendInfo carries the active backend name and model
`resolve_backend` SHALL return a `BackendInfo(name: str, model: str)` frozen dataclass alongside the backend instance. `name` is the config key (`"mistral"`, `"anthropic"`, `"openrouter"`); `model` is the model name string used for that backend.

#### Scenario: BackendInfo reflects the selected backend
- **WHEN** `resolve_backend` selects the `"anthropic"` backend with model `"claude-haiku-4-5-20251001"`
- **THEN** the returned `BackendInfo` SHALL have `name="anthropic"` and `model="claude-haiku-4-5-20251001"`

### Requirement: Anthropic backend uses ANTHROPIC_API_KEY and defaults to claude-haiku-4-5-20251001
The system SHALL provide a `create_anthropic_backend(model: str)` factory in `llm/anthropic.py` that reads `ANTHROPIC_API_KEY` from the environment. The default model in `configs/codemoo.toml` SHALL be `"claude-haiku-4-5-20251001"`.

#### Scenario: Anthropic backend raises BackendUnavailableError without key
- **WHEN** `create_anthropic_backend()` is called and `ANTHROPIC_API_KEY` is not set
- **THEN** it SHALL raise `BackendUnavailableError`

### Requirement: OpenRouter backend uses OPENROUTER_API_KEY and the OpenAI-compatible endpoint
The system SHALL provide a `create_openrouter_backend(model: str)` factory in `llm/openrouter.py` that reads `OPENROUTER_API_KEY` from the environment and connects to `https://openrouter.ai/api/v1` via the `openai` SDK. The default model in `configs/codemoo.toml` SHALL be `"z-ai/glm-4.5-air:free"`.

#### Scenario: OpenRouter backend raises BackendUnavailableError without key
- **WHEN** `create_openrouter_backend()` is called and `OPENROUTER_API_KEY` is not set
- **THEN** it SHALL raise `BackendUnavailableError`
