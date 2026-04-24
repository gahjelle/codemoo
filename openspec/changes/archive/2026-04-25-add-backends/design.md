## Context

`llm/backend.py` currently contains a single concrete Mistral backend that is hardcoded in every call site across both frontends. `ToolDef` carries a raw `schema: dict` in Mistral/OpenAI wire format, which cannot be reused for Anthropic (different shape). Three separate `_tool_name()` helpers extract the tool name by drilling into this dict.

Adding Anthropic and OpenRouter requires:
1. A backend-neutral tool representation that each provider converts to its own wire format
2. A factory abstraction that selects the right backend at startup
3. A way to surface which backend is active in the UI

## Goals / Non-Goals

**Goals:**
- Three working backends: Mistral, Anthropic, OpenRouter
- Config-driven primary + ordered fallback selection at startup
- `ToolDef` restructured to be backend-neutral with per-backend converters
- Backend name and model visible in TUI at all times

**Non-Goals:**
- Streaming responses
- Per-bot backend selection
- Runtime backend switching after startup
- Provider-specific features (extended thinking, model routing, etc.)

## Decisions

### One module per backend (`llm/mistral.py`, `llm/anthropic.py`, `llm/openrouter.py`)

Anthropic's wire format is structurally different from Mistral/OpenAI: system messages are a separate `system=` parameter (not a list entry), tool schemas use `input_schema` instead of `parameters`, and tool result messages carry `tool_use_id` instead of `tool_call_id`. Putting all backends in one file would interleave three sets of serialization helpers with no cohesion benefit. Separate modules make each backend self-contained and easy to add or remove.

**Alternatives considered**: Single `llm/backends.py` — rejected because the per-provider divergence outweighs the colocation benefit.

### `BackendUnavailableError` for missing API key

Each `create_*_backend()` raises a custom `BackendUnavailableError` (not bare `ValueError`) when its API key is absent. `resolve_backend()` catches only `BackendUnavailableError`, so network errors and programming mistakes propagate normally. This avoids accidentally swallowing unrelated `ValueError`s during the fallback loop.

**Alternatives considered**: Checking for env var presence before calling the factory — equivalent but would duplicate the env var name in the factory and the caller.

### `resolve_backend(config)` returns `tuple[ToolLLMBackend, BackendInfo]`

The factory knows which backend it selected and what model it configured — the call sites shouldn't have to re-derive that for display purposes. `BackendInfo(name, model)` is a plain frozen dataclass that carries just enough for the status bar and logging. It lives in `llm/factory.py` alongside the factory.

**Alternatives considered**: Adding `.name` and `.model` attributes to the backend protocol — would couple the display concern into the protocol and all backend implementations.

### OpenAI SDK for OpenRouter

OpenRouter explicitly advertises OpenAI API compatibility. Using `openai.AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)` requires no custom HTTP code and reuses the same serialization as the OpenAI wire format (which is identical to the Mistral format). Adds `openai` as a dependency but eliminates all custom deserialization for a third backend.

**Alternatives considered**: Direct `httpx` — more control, no extra dependency, but requires hand-rolling response parsing.

### Free functions `_tool_schema(tool: ToolDef) -> dict` per backend module

`core/tools` must not import from `llm` backends (would create a circular dependency and couple the core to specific providers). Methods on `ToolDef` would require the same — `ToolDef` lives in `core` and cannot reference `llm`. Free functions in each backend module keep `core` fully provider-agnostic.

**Alternatives considered**: A registry mapping backend names to converter functions in `core/tools` — over-engineered for the current scope.

### `ToolParam` as a flat dataclass (`name`, `description`, `type="string"`, `required=True`)

All four current tools use only flat string parameters. A flat model covers 100% of current usage and makes tool definitions significantly more readable. The `type` field accepts any JSON Schema type string, so non-string parameters can be added per-tool without changing the dataclass. Complex nested schemas are not needed now and can be added via an `extra_schema` escape hatch if ever required.

### `tool_calls_json` round-trip is per-backend

When `complete_step` returns a `ToolUse`, the `assistant_message` carries `tool_calls_json` — a serialized representation reinjected on the next request. Anthropic's format differs from Mistral's. Since the same backend instance handles all turns in a conversation, each backend only ever reads its own serialized format. No cross-backend compatibility is needed.

## Risks / Trade-offs

- **Anthropic tool round-trip complexity** → The Anthropic message format for tool results uses `content` as a list, not a string. The `Message` dataclass currently has `content: str`. The Anthropic backend will need to handle this when serializing tool result messages, possibly by JSON-encoding the content list into the `content` string and decoding it internally.

- **OpenRouter model availability** → Free-tier models (e.g. `z-ai/glm-4.5-air:free`) may be rate-limited or removed. This is a config value, easily changed. No mitigation needed in code.

- **`uv add` changes lockfile** → Adding `anthropic` and `openai` will update `uv.lock`. Both are stable, well-maintained packages with no known compatibility issues with the current stack.

## Migration Plan

1. Add `anthropic` and `openai` dependencies via `uv add`
2. Restructure `ToolDef` and update all tool definitions and callers (this is self-contained within the codebase — no external API changes)
3. Add backend modules and factory; delete `llm/backend.py`
4. Update config schema and `codemoo.toml`
5. Update frontends to use `resolve_backend(config)`
6. Add `BackendStatus` widget and wire into `ChatApp`

Rollback: revert to `llm/backend.py` with hardcoded Mistral and old `ToolDef.schema` — no database or external state involved.

## Open Questions

- Should `BackendStatus` also appear in `demoo` (the CLI frontend)? Currently out of scope — it's a TUI widget. The CLI could print the backend info to stdout on startup as a separate concern.
