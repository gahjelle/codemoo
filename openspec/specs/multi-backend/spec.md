# Spec: multi-backend

## Purpose

TBD — Defines the `resolve_backend` factory, the `BackendInfo` value type, backend fallback logic, and concrete backend factories for Anthropic and OpenRouter in addition to Mistral.

## Requirements

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

### Requirement: BackendInfo carries the active backend name and model
`resolve_backend` SHALL return a `BackendInfo(name: str, model: str)` frozen dataclass alongside the backend instance. `name` is the config key (`"mistral"`, `"anthropic"`, `"openrouter"`, `"openai"`, `"google"`, `"ollama"`); `model` is the model name string used for that backend.

#### Scenario: BackendInfo reflects the selected backend
- **WHEN** `resolve_backend` selects the `"anthropic"` backend with model `"claude-haiku-4-5-20251001"`
- **THEN** the returned `BackendInfo` SHALL have `name="anthropic"` and `model="claude-haiku-4-5-20251001"`

### Requirement: Anthropic backend uses ANTHROPIC_API_KEY and defaults to claude-haiku-4-5-20251001
The system SHALL provide a `create_anthropic_backend(model: str)` factory in `llm/anthropic.py` that reads `ANTHROPIC_API_KEY` from the environment. The default model in `configs/codemoo.toml` SHALL be `"claude-haiku-4-5-20251001"`.

#### Scenario: Anthropic backend raises BackendUnavailableError without key
- **WHEN** `create_anthropic_backend()` is called and `ANTHROPIC_API_KEY` is not set
- **THEN** it SHALL raise `BackendUnavailableError`

### Requirement: OpenRouter backend uses OPENROUTER_API_KEY and base_url from config
The system SHALL provide a `create_openrouter_backend(model: str, base_url: str)` factory in `llm/openrouter.py` that reads `OPENROUTER_API_KEY` from the environment and raises `BackendUnavailableError` if it is absent. The `base_url` parameter is required and SHALL be sourced from `BackendConfig.base_url` in `codemoo.toml`; there is no hardcoded fallback URL in code.

#### Scenario: OpenRouter backend raises BackendUnavailableError without key
- **WHEN** `create_openrouter_backend()` is called and `OPENROUTER_API_KEY` is not set
- **THEN** it SHALL raise `BackendUnavailableError`

#### Scenario: base_url from config is used
- **WHEN** `BackendConfig.base_url = "https://openrouter.ai/api/v1"` is set in TOML
- **THEN** the factory SHALL construct the client with that URL
