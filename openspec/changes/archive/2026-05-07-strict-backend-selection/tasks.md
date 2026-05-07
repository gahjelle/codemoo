## 1. Schema changes

- [x] 1.1 In `ModelsConfig` (`src/codemoo/config/schema.py`), change `backend: ModelBackend` to `backend: ModelBackend | None = None`
- [x] 1.2 Add a `field_validator("backend", mode="before")` that converts `""` to `None`

## 2. Config file changes

- [x] 2.1 In `codemoo.toml` `[models]` section, change `backend = "mistral"` to `backend = ""` with a comment explaining the sentinel

## 3. Factory changes

- [x] 3.1 In `resolve_backend()` (`src/codemoo/llm/factory.py`), replace the candidates list: `[config.models.backend] if config.models.backend is not None else config.models.fallbacks`

## 4. Tests

- [x] 4.1 Add a test: explicit backend available → returned, no fallback attempted
- [x] 4.2 Add a test: explicit backend unavailable → `BackendUnavailableError` raised, no fallback
- [x] 4.3 Add a test: no explicit backend → first available fallback returned
- [x] 4.4 Add a test: `config.models.backend` is `None` when `CODEMOO_BACKEND` is unset (schema validator test)
- [x] 4.5 Add a test: `config.models.backend` is `None` when TOML has `backend = ""` and env var is absent

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/`
- [x] 5.2 Run `uv run ruff check src/ tests/`
- [x] 5.3 Run `uv run ty check src/ tests/`
- [x] 5.4 Run `uv run pytest`

## 6. Documentation

- [x] 6.1 Review `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md`; update any references to `CODEMOO_BACKEND` or the backend selection behaviour if needed
