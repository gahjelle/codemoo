## 1. Config Schema

- [x] 1.1 Add `"openai"`, `"google"`, `"ollama"` to the `ModelBackend` literal in `config/schema.py`
- [x] 1.2 Add `base_url: str | None = None` to `BackendConfig` in `config/schema.py`

## 2. Config TOML

- [x] 2.1 Add `base_url = "https://openrouter.ai/api/v1"` to `[models.backends.openrouter]` in `codemoo.toml`
- [x] 2.2 Add `[models.backends.ollama]` entry (`model_name = "llama3.2"`, `base_url = "http://localhost:11434/v1"`)
- [x] 2.3 Add `[models.backends.google]` entry (`model_name = "gemini-2.0-flash"`, `base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"`)
- [x] 2.4 Add `[models.backends.openai]` entry (`model_name = "gpt-4o-mini"`)
- [x] 2.5 Update `fallbacks` list to `["mistral", "ollama", "openrouter", "google", "anthropic", "openai"]`

## 3. Update OpenRouter Backend

- [x] 3.1 Remove hardcoded `_OPENROUTER_BASE_URL` constant from `llm/openrouter.py`
- [x] 3.2 Change `create_openrouter_backend()` signature to `(model: str, base_url: str)` — URL comes from config only

## 4. New OpenAI Backend

- [x] 4.1 Create `src/codemoo/llm/openai.py` with `_OpenAIBackend(OpenAILikeBackend)` and `create_openai_backend(model, base_url)`
- [x] 4.2 Read `OPENAI_API_KEY`; raise `BackendUnavailableError` if absent
- [x] 4.3 Pass `base_url` to `openai.AsyncOpenAI` constructor when not `None`

## 5. New Google Backend

- [x] 5.1 Create `src/codemoo/llm/google.py` with `_GoogleBackend(OpenAILikeBackend)` and `create_google_backend(model, base_url)`
- [x] 5.2 Read `GOOGLE_API_KEY`; raise `BackendUnavailableError` if absent
- [x] 5.3 Pass `base_url` to `openai.AsyncOpenAI` constructor

## 6. New Ollama Backend

- [x] 6.1 Create `src/codemoo/llm/ollama.py` with `_OllamaBackend(OpenAILikeBackend)` and `create_ollama_backend(model, base_url)`
- [x] 6.2 Read `OLLAMA_API_KEY`; default to `"ollama"` silently when absent
- [x] 6.3 Ping `GET {base_url}/models` with `httpx.Client(timeout=2.0)`; raise `BackendUnavailableError` on connection error or timeout
- [x] 6.4 Pass `base_url` and key to `openai.AsyncOpenAI` constructor

## 7. Update Factory

- [x] 7.1 Thread `backend_cfg.base_url` through `_create()` to all `create_*_backend()` calls that accept it
- [x] 7.2 Add dispatch cases for `"openai"`, `"google"`, `"ollama"` in `_create()`

## 8. Env Var Overrides

- [x] 8.1 Add `"OPENAI_MODEL": "models.backends.openai.model_name"` to the configaroo mappings in `config/__init__.py`
- [x] 8.2 Add `"GOOGLE_MODEL": "models.backends.google.model_name"` to the configaroo mappings in `config/__init__.py`
- [x] 8.3 Add `"OLLAMA_MODEL": "models.backends.ollama.model_name"` to the configaroo mappings in `config/__init__.py`

## 9. Tests

- [x] 9.1 Add tests for `create_openai_backend`: key present, key absent
- [x] 9.2 Add tests for `create_openai_backend` with custom `base_url`
- [x] 9.3 Add tests for `create_google_backend`: key present, key absent
- [x] 9.4 Add tests for `create_ollama_backend`: server reachable, server unreachable (mock httpx), key defaulting
- [x] 9.5 Add tests for `BackendConfig` with and without `base_url`
- [x] 9.6 Add tests for `_create()` dispatching `"openai"`, `"google"`, `"ollama"`

## 10. Documentation

- [x] 10.1 Update the `CODEMOO_BACKEND` description in `README.md` to list all six backend names
- [x] 10.2 Add rows to the LLM Backends table in `README.md` for `OPENAI_API_KEY`, `CODEMOO_OPENAI_MODEL`, `GOOGLE_API_KEY`, `CODEMOO_GOOGLE_MODEL`, `OLLAMA_API_KEY`, `CODEMOO_OLLAMA_MODEL`
- [x] 10.3 Update the requirements list at the top of `README.md` (currently lists Mistral/OpenRouter/Anthropic only)
- [x] 10.4 Read `PLANS.md`, `BOTS.md`, `AGENTS.md` and update any references to supported backends

## 11. Verification

- [x] 11.1 `uv run ruff format src/ tests/`
- [x] 11.2 `uv run ruff check src/ tests/`
- [x] 11.3 `uv run ty check src/ tests/`
- [x] 11.4 `uv run pytest`
