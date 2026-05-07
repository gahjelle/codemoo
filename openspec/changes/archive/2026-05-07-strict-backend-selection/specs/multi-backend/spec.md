## MODIFIED Requirements

### Requirement: resolve_backend uses strict mode when an explicit backend is configured
The system SHALL provide a `resolve_backend(config, tracer=None)` factory function in `llm/factory.py`. When `config.models.backend` is not `None`, it SHALL attempt only that backend and SHALL NOT catch `BackendUnavailableError` — the error propagates directly to the caller. It SHALL accept an optional `tracer: Tracer | None = None` parameter and thread it through `_create()`.

#### Scenario: Explicit backend available — returned directly
- **WHEN** `config.models.backend = "openai"` and the OpenAI backend is available
- **THEN** `resolve_backend()` SHALL return the OpenAI backend and `BackendInfo(name="openai", ...)`

#### Scenario: Explicit backend unavailable — error propagates
- **WHEN** `config.models.backend = "openai"` and `OPENAI_API_KEY` is not set
- **THEN** `resolve_backend()` SHALL raise `BackendUnavailableError` without attempting any fallback

#### Scenario: Tracer threaded through in strict mode
- **WHEN** `resolve_backend(config, tracer=my_tracer)` is called with an explicit backend
- **THEN** the returned backend SHALL be constructed with `tracer=my_tracer`

### Requirement: resolve_backend falls back through config.models.fallbacks when no explicit backend is set
When `config.models.backend` is `None`, `resolve_backend` SHALL try each entry in `config.models.fallbacks` in order, catching `BackendUnavailableError` per step and moving to the next candidate. It SHALL return the first backend that succeeds.

#### Scenario: First fallback available — returned
- **WHEN** `config.models.backend` is `None` and the first entry in `config.models.fallbacks` is available
- **THEN** `resolve_backend` SHALL return that backend

#### Scenario: First fallback unavailable, second available — second returned
- **WHEN** `config.models.backend` is `None`, the first fallback raises `BackendUnavailableError`, and the second is available
- **THEN** `resolve_backend` SHALL return the second fallback backend

#### Scenario: All fallbacks unavailable — error raised
- **WHEN** `config.models.backend` is `None` and all fallback backends raise `BackendUnavailableError`
- **THEN** `resolve_backend` SHALL raise an exception describing all attempted backends

#### Scenario: resolve_backend called without tracer in fallback mode
- **WHEN** `resolve_backend(config)` is called with `config.models.backend = None`
- **THEN** the backend SHALL be constructed with `tracer=None`
