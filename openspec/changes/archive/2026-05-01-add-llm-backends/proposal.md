## Why

Codemoo currently supports only Mistral, Anthropic, and OpenRouter as LLM backends. Adding OpenAI, Google Gemini, and Ollama gives users more choice — including a free local option — and makes the demo more compelling for audiences who already have keys for these providers.

## What Changes

- **New backend: OpenAI** — `llm/openai.py` using `OPENAI_API_KEY`; reuses `OpenAILikeBackend`
- **New backend: Google Gemini** — `llm/google.py` using `GOOGLE_API_KEY` against Google's OpenAI-compatible endpoint; reuses `OpenAILikeBackend`
- **New backend: Ollama** — `llm/ollama.py` for local Ollama servers; availability detected by pinging `GET /models` (no API key required by default)
- **`BackendConfig` gains `base_url`** — optional field that allows provider URLs to be set in TOML; OpenRouter's hardcoded URL moves here; enables Azure AI Foundry and other OpenAI-compatible endpoints via the `openai` backend without a dedicated backend type
- **Updated fallback order** — `mistral, ollama, openrouter, google, anthropic, openai`
- **Factory and config** — `factory.py` and `schema.py` updated to register the three new names

## Non-goals

- Native Google `google-generativeai` SDK (use OpenAI-compatible endpoint instead; SDK can be added later if needed)
- A named `azure` backend (Azure AI Foundry works via `base_url` override on the `openai` backend)
- Multiple instances of the same provider in the fallback chain (would require a schema refactor with a `provider` field)
- Streaming responses
- Model listing or validation at startup

## Capabilities

### New Capabilities

- `openai-backend`: OpenAI backend using `OPENAI_API_KEY`; subclass of `OpenAILikeBackend`; supports optional `base_url` for Azure AI Foundry and compatible endpoints
- `google-backend`: Google Gemini backend using `GOOGLE_API_KEY` against the OpenAI-compatible Gemini endpoint; subclass of `OpenAILikeBackend`
- `ollama-backend`: Ollama local-server backend; availability detected by a synchronous HTTP ping to `GET {base_url}/models` via `httpx`; API key defaults to `"ollama"` silently when unset

### Modified Capabilities

- `multi-backend`: New backends added to the registry; default fallback order updated; `BackendConfig` gains an optional `base_url` field; `create_openrouter_backend` and all new factories accept a `base_url` parameter passed from config
- `openai-backend-base`: Concrete subclasses now receive `base_url` from their factory function and pass it to the OpenAI client constructor

## Impact

- `src/codemoo/config/schema.py` — `ModelBackend` literal extended; `BackendConfig.base_url` added
- `src/codemoo/config/codemoo.toml` — new backend entries; OpenRouter `base_url` moved to config; fallback order updated
- `src/codemoo/llm/factory.py` — three new dispatch cases; `base_url` threaded through
- `src/codemoo/llm/openrouter.py` — hardcoded URL removed; `base_url` param added
- `src/codemoo/llm/openai.py` — new file
- `src/codemoo/llm/google.py` — new file
- `src/codemoo/llm/ollama.py` — new file
- No new dependencies (`httpx` and `openai` already present)
