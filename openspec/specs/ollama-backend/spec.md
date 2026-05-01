# Spec: ollama-backend

## Purpose

TBD — Defines the Ollama backend factory and its concrete `_OllamaBackend` class, enabling Codemoo to use a locally running (or remote) Ollama server as an LLM backend. Availability is determined by pinging the server rather than by checking an API key.

## Requirements

### Requirement: Ollama backend availability is detected by pinging GET /models
The system SHALL provide a `create_ollama_backend(model: str, base_url: str)` factory in `llm/ollama.py`. Because Ollama does not mandate an API key, availability SHALL be determined by issuing a synchronous `GET {base_url}/models` request via `httpx.Client` with a 2-second timeout. If the request fails with a connection error or timeout, the factory SHALL raise `BackendUnavailableError`.

#### Scenario: Ollama is running — backend created
- **WHEN** `create_ollama_backend(model, base_url)` is called and the Ollama server responds to `GET {base_url}/models`
- **THEN** it SHALL return an `LLMBackend` instance

#### Scenario: Ollama is not running — BackendUnavailableError raised
- **WHEN** `create_ollama_backend()` is called and the server is unreachable or times out
- **THEN** it SHALL raise `BackendUnavailableError` so the fallback loop continues

### Requirement: Ollama API key defaults to "ollama" when OLLAMA_API_KEY is unset
The factory SHALL read `OLLAMA_API_KEY` from the environment. If the variable is absent it SHALL silently use `"ollama"` as the key (the Ollama convention for unauthenticated local servers) rather than raising an error. An explicit `OLLAMA_API_KEY` is used as-is, supporting authenticated remote Ollama deployments.

#### Scenario: No key set — defaults to "ollama"
- **WHEN** `OLLAMA_API_KEY` is not set
- **THEN** the client SHALL be constructed with `api_key="ollama"` and SHALL NOT raise `BackendUnavailableError`

#### Scenario: Key set — used verbatim
- **WHEN** `OLLAMA_API_KEY=secret` is set
- **THEN** the client SHALL be constructed with `api_key="secret"`

### Requirement: Ollama backend is a subclass of OpenAILikeBackend
`_OllamaBackend` SHALL inherit from `OpenAILikeBackend` and implement only `_call()`.

#### Scenario: Text completion
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL return the response text as `str`

#### Scenario: Tool call response
- **WHEN** `complete(messages, tools=[...])` is called and the model requests a tool
- **THEN** it SHALL return a `ToolUse` instance
