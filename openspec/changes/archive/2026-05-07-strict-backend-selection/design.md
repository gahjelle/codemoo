## Context

`resolve_backend()` currently builds a single candidate list from `[config.models.backend, *config.models.fallbacks]` and walks it, catching `BackendUnavailableError` at each step. The `backend` field in TOML defaults to `"mistral"`, making Mistral the effective primary. When a user sets `CODEMOO_BACKEND=openai` but lacks the API key, the factory silently continues to the next fallback — the user gets Mistral with no indication anything went wrong.

The configaroo `add_envs()` call raises `MissingEnvironmentVariableError` if an env var mapping is declared but the env var is absent **and** the key does not already exist in the config data. Removing `backend` from the TOML would therefore break startup for all users who don't set `CODEMOO_BACKEND`.

## Goals / Non-Goals

**Goals:**
- `CODEMOO_BACKEND` set → strict: only that backend is attempted; error propagates on failure
- `CODEMOO_BACKEND` unset → fallback: walk `fallbacks` list in order, return first available (current behaviour)
- Config load must not raise for users who never set `CODEMOO_BACKEND`

**Non-Goals:**
- Changing which backends exist or their default models
- Changing the fallback list order
- Supporting partial fallbacks (e.g., "try openai, then only anthropic")

## Decisions

### Empty string as TOML sentinel, normalised to `None` by Pydantic

The TOML key `backend = ""` must remain so configaroo sees the key as present and skips the `MissingEnvironmentVariableError` guard. Downstream code shouldn't have to handle `""` — a Pydantic `field_validator(mode="after")` on `ModelsConfig.backend` converts `""` to `None` at parse time. The field type becomes `ModelBackend | None = None`.

**Alternative considered:** keep `backend: ModelBackend | Literal[""]` throughout. Rejected — `Literal[""]` bleeds into factory logic and type guards everywhere.

**Alternative considered:** remove the `BACKEND` env-var mapping from `add_envs()` and read `os.getenv("CODEMOO_BACKEND")` directly in `resolve_backend()`. Rejected — breaks consistency with how all other env overrides work; the key should stay in `add_envs`.

### Single candidates list, not a branch in `resolve_backend()`

The candidates list is built differently depending on whether `backend` is set, then the existing walk loop runs unchanged:

```python
candidates = (
    [config.models.backend]
    if config.models.backend is not None
    else config.models.fallbacks
)
```

When `backend` is set, the single-element list means the loop has exactly one shot — if `BackendUnavailableError` is caught, there are no further candidates and the existing `ValueError("No LLM backend available. Tried: ...")` is raised with the backend name in the "Tried:" list. No new branching inside the loop body, no new exception types for callers.

This was confirmed safe by checking all call sites of `resolve_backend` (`cli.py`, `tui.py`): none of them catch `BackendUnavailableError` specifically, so the exception type reaching callers doesn't matter.

**Alternative considered:** explicit branch — `if config.models.backend is not None: attempt only that backend, propagate error; else: walk fallbacks`. Rejected — the list approach achieves the same semantics with less code and keeps the loop logic intact.

## Risks / Trade-offs

- **Breaking for implicit reliers on fallback** → Users who set `CODEMOO_BACKEND` expecting fallback protection will now see an error. This is intentional; the "Tried:" section of the error message names the backend and its failure reason clearly.
- **Empty string in TOML is non-obvious** → A comment in `codemoo.toml` on the `backend` line will explain the sentinel convention.

## Migration Plan

No data migration required. On upgrade:
1. TOML changes from `backend = "mistral"` to `backend = ""` — the first available backend in `fallbacks` is Mistral, so effective default is unchanged.
2. Users who set `CODEMOO_BACKEND` to an unavailable backend will see an error on startup rather than silent fallback.

No rollback complexity — reverting is a single-line TOML change plus the schema/factory revert.
