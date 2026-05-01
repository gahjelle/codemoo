## Context

Codemoo's LLM layer has a clean port/adapter architecture: `LLMBackend` protocol in `core/backend.py`, an `OpenAILikeBackend` base class in `llm/openai_like.py` that handles all OpenAI-format serialization and tool-call parsing, and thin concrete backends (`mistral.py`, `openrouter.py`) that only implement `_call()`. Anthropic sits outside this hierarchy due to its distinct wire format.

The factory (`llm/factory.py`) dispatches by backend name and wraps creation in a `BackendUnavailableError` catch so the fallback loop works cleanly. `BackendConfig` currently holds only `model_name`; the OpenRouter base URL is hardcoded in `openrouter.py`.

Adding OpenAI and Google requires minimal code because `OpenAILikeBackend` does all the work — new backends are ~30 lines each. Ollama is the interesting case because it lacks a mandatory API key; a different availability signal is needed.

## Goals / Non-Goals

**Goals:**
- Add `openai`, `google`, and `ollama` as named backends usable in the fallback chain
- Make provider base URLs configurable via `BackendConfig.base_url` (replaces OpenRouter's hardcoded constant)
- Use a synchronous HTTP ping for Ollama availability, keeping the factory synchronous
- No new dependencies

**Non-Goals:**
- Native Google SDK (`google-generativeai`)
- A named `azure` backend (Azure AI Foundry is handled by `base_url` override on `openai`)
- Multiple instances of the same provider in one config
- Streaming, model validation, or async factory

## Decisions

### OpenAI and Google: subclass `OpenAILikeBackend` directly

Both providers speak the OpenAI wire format. `openai.AsyncOpenAI` (already a dependency) works for both — standard endpoint for OpenAI, Google's `generativelanguage.googleapis.com/v1beta/openai/` for Gemini. Each new file is a ~30-line clone of `openrouter.py` with a different env-var name and no hardcoded base URL (URL comes from config).

**Alternative considered**: native `google-generativeai` SDK for Google. Rejected because it adds a dependency, requires new serialization logic (~100 lines), and the OpenAI-compatible endpoint covers all current use cases. Easily added later.

### Ollama availability: synchronous HTTP ping instead of key check

Ollama doesn't mandate an API key, so the existing "env var absent → `BackendUnavailableError`" signal doesn't apply. Options considered:

1. **Require `OLLAMA_API_KEY`** — breaks UX for the common local case with no key
2. **Always available** — tries to call a server that may not be running
3. **Synchronous HTTP ping to `GET {base_url}/models`** ← chosen

The ping uses `httpx.Client` (already a dependency) with a 2-second timeout. `ConnectionError` or `TimeoutException` raises `BackendUnavailableError`, keeping the fallback loop behaviour identical to the key-check path. `OLLAMA_API_KEY` is still read from env for users running auth'd remote Ollama, but silently defaults to `"ollama"` (the Ollama convention) when absent.

**Trade-off**: the ping adds ~2 s latency at startup when Ollama is unavailable. This is acceptable because the factory is called once at startup, and the 2 s is bounded.

### `base_url` in `BackendConfig`

`BackendConfig` gains `base_url: str | None = None`. Backends that need a custom URL (OpenRouter, Google, Ollama) read it from config; backends that don't (OpenAI with its SDK default, Anthropic) leave it `None`. The factory passes `base_url` to each `create_*_backend()` function.

This also makes OpenRouter's URL visible and overridable in TOML, which is cleaner than a module-level constant.

**Alternative considered**: `OLLAMA_BASE_URL` env var. Rejected because it fragments configuration across env vars and TOML, and `base_url` in config is already the right location for deployment-specific URLs.

### File naming: `openai.py` is safe

Python 3's absolute imports mean `import openai` inside `codemoo/llm/openai.py` resolves to the installed top-level package, not the current module. The naming stays consistent with `mistral.py`, `openrouter.py`, `anthropic.py`. Callers use `from codemoo.llm.openai import create_openai_backend`, which is unambiguous.

### Azure AI Foundry: not a named backend

Foundry serverless endpoints speak the OpenAI wire format with a key and base URL — exactly what the `openai` backend supports with `base_url` set. A named `azure` backend would duplicate ~30 lines for no functional gain. The one limitation (can't have both standard OpenAI and Azure Foundry in the same fallback chain) is acceptable; the schema would need a `provider` field refactor to solve it, which is out of scope.

## Risks / Trade-offs

- **Ping latency on Ollama miss**: ~2 s per unavailable Ollama entry in the fallback chain. Mitigation: keep Ollama high in the fallback order so it's tried before slower cloud providers; the timeout is bounded.
- **Google's OpenAI-compatible endpoint**: relatively new (2024) and may have undocumented schema quirks for advanced tool-use patterns. Mitigation: basic tool calling is well-tested; complex cases can prompt a native SDK migration later.
- **`base_url` is required for OpenRouter/Google/Ollama**: if a user omits it from TOML, the backend will fail at runtime rather than config-parse time. Mitigation: `codemoo.toml` ships with correct defaults for all three.

## Migration Plan

No breaking changes for new backends. OpenRouter's `base_url` moves from a hardcoded module constant to `codemoo.toml`; the code no longer carries a fallback URL. Existing configs without the new backend names continue to work unchanged.
