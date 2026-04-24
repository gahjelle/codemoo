## Why

Codemoo is hardwired to Mistral: every call site creates a Mistral backend directly, making it impossible to run without a `MISTRAL_API_KEY`. Adding Anthropic and OpenRouter backends — with config-driven fallback — lets the demo work regardless of which API key is available, and makes the multi-provider landscape visible to audiences watching the demo.

## What Changes

- **New**: `llm/mistral.py` — Mistral backend extracted from `llm/backend.py`
- **New**: `llm/anthropic.py` — Anthropic backend (default model: `claude-haiku-4-5-20251001`)
- **New**: `llm/openrouter.py` — OpenRouter backend via OpenAI-compatible API (default model: `z-ai/glm-4.5-air:free`)
- **New**: `llm/factory.py` — `resolve_backend(config)` with ordered fallback; `BackendInfo` dataclass
- **Removed**: `llm/backend.py` (contents moved to `llm/mistral.py`)
- **BREAKING**: `ToolDef.schema: dict` replaced with structured fields (`name`, `description`, `parameters: list[ToolParam]`); all tool definitions rewritten
- **New**: `chat/backend_status.py` — always-visible footer widget showing active backend and model
- **Modified**: `chat/app.py` — `ChatApp` gains `backend_info: BackendInfo` parameter; `BackendStatus` added to layout
- **Modified**: `config/schema.py` — `ModelBackend` extended to `Literal["mistral", "anthropic", "openrouter"]`
- **Modified**: `configs/codemoo.toml` — anthropic and openrouter backend entries added
- **Modified**: both frontends — hardcoded `create_mistral_backend` calls replaced with `resolve_backend(config)`
- **New dependencies**: `anthropic`, `openai` (added via `uv add`)

## Capabilities

### New Capabilities

- `multi-backend`: Multiple LLM provider backends with config-driven selection and ordered fallback at startup
- `structured-tool-def`: Backend-neutral `ToolDef` with structured fields; per-backend wire-format converters
- `backend-status-bar`: Always-visible TUI footer showing the active backend name and model

### Modified Capabilities

- `llm-backend`: Factory interface changes — `create_mistral_backend` is no longer the public entry point; `resolve_backend` becomes the canonical way to obtain a backend. `BackendUnavailableError` replaces bare `ValueError` for missing-key failures.
- `tool-definitions`: `ToolDef.schema` dict replaced with structured `name`, `description`, `parameters` fields. The `ToolParam` type is introduced.

## Impact

- `core/tools/__init__.py` — all four `ToolDef` instances rewritten
- `core/bots/general_tool_bot.py`, `core/bots/agent_bot.py`, `chat/slides.py` — `_tool_name()` helpers removed; replaced with `tool.name`
- `frontends/tui.py`, `frontends/cli.py` — backend creation updated
- `pyproject.toml` — two new dependencies (`anthropic`, `openai`)

## Non-goals

- Streaming responses
- Per-bot backend selection (all bots in a session share one backend)
- Runtime backend switching after startup
- Supporting provider-specific features (e.g. Anthropic extended thinking, OpenRouter model routing)
