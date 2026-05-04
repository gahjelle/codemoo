## MODIFIED Requirements

### Requirement: resolve_backend selects the configured primary backend at startup
The system SHALL provide a `resolve_backend(config, tracer=None)` factory function in `llm/factory.py` that reads `config.models.backend` and attempts to create that backend. It SHALL accept an optional `tracer: Tracer | None = None` parameter and thread it through `_create()` to each backend factory. On success it SHALL return a `tuple[LLMBackend, BackendInfo]`. It SHALL NOT catch network errors — only `BackendUnavailableError`.

#### Scenario: Primary backend is available, tracer threaded through
- **WHEN** `resolve_backend(config, tracer=my_tracer)` is called and the primary backend is available
- **THEN** it SHALL return a backend constructed with `tracer=my_tracer`

#### Scenario: resolve_backend called without tracer (existing behavior unchanged)
- **WHEN** `resolve_backend(config)` is called with no tracer argument
- **THEN** the backend SHALL be constructed with `tracer=None` and behavior SHALL be identical to before this change

### Requirement: _create() threads Tracer to each backend factory
The internal `_create(name, model, base_url, tracer=None)` function SHALL pass `tracer` to every `create_*_backend()` call. Each factory function SHALL accept `tracer: Tracer | None = None` and pass it to the backend constructor.

#### Scenario: Tracer reaches the backend constructor
- **WHEN** `resolve_backend(config, tracer=t)` dispatches to `create_anthropic_backend(model, tracer=t)`
- **THEN** the returned `_AnthropicBackend` SHALL have `self._tracer is t`
