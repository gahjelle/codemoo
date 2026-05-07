## Why

When a user explicitly sets `CODEMOO_BACKEND=openai` but that backend is unavailable, the system silently falls back to Mistral (or whatever is next in the fallback list) instead of reporting an error — a confusing experience that may go unnoticed entirely. The fix is to treat `CODEMOO_BACKEND` as a strict override: if set, use only that backend and raise loudly on failure; if unset, walk the fallback list as before.

## What Changes

- `codemoo.toml`: `backend = "mistral"` → `backend = ""` (empty string signals "no explicit backend; use fallbacks")
- `ModelsConfig.backend`: type changes from required `ModelBackend` to optional `ModelBackend | None = None`, with a Pydantic after-validator that converts `""` → `None` at config load time
- `resolve_backend()`: branches on `config.models.backend`:
  - **Strict mode** (backend is set): attempt only that backend; let `BackendUnavailableError` propagate — no silent fallback
  - **Fallback mode** (backend is `None`): walk `config.models.fallbacks` in order and return the first available (current behaviour)

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities

- `multi-backend`: `resolve_backend` selection logic changes — strict-vs-fallback branching replaces the single unified candidate list; the requirement that the primary backend is always first in the candidate list is removed
- `env-model-config`: `CODEMOO_BACKEND` behaviour changes — when set it must succeed; when unset the key must still exist in TOML (as `""`) so configaroo does not raise `MissingEnvironmentVariableError`

## Impact

- `src/codemoo/config/codemoo.toml` — `[models]` section
- `src/codemoo/config/schema.py` — `ModelsConfig`
- `src/codemoo/llm/factory.py` — `resolve_backend()`
- No public API changes; no new dependencies
- Users who relied on silent fallback when `CODEMOO_BACKEND` was set will now see an error instead — intentional breaking behaviour change

## Non-goals

- Changing the fallback list itself or which backends are supported
- Introducing a way to disable fallbacks without setting `CODEMOO_BACKEND`
- Changing how individual model names are overridden via env vars (`CODEMOO_MISTRAL_MODEL`, etc.)
