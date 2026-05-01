# Spec: google-backend

## Purpose

TBD — Defines the Google backend factory and its concrete `_GoogleBackend` class, enabling Codemoo to use the Google Gemini API via its OpenAI-compatible endpoint as an LLM backend.

## Requirements

### Requirement: Google backend uses GOOGLE_API_KEY against the OpenAI-compatible Gemini endpoint
The system SHALL provide a `create_google_backend(model: str, base_url: str)` factory in `llm/google.py` that reads `GOOGLE_API_KEY` from the environment and raises `BackendUnavailableError` if it is absent. It SHALL construct an `openai.AsyncOpenAI` client pointed at the provided `base_url` (canonically `https://generativelanguage.googleapis.com/v1beta/openai/`, set in `codemoo.toml`).

#### Scenario: Backend created when key is present
- **WHEN** `GOOGLE_API_KEY` is set and `create_google_backend(model, base_url)` is called
- **THEN** it SHALL return an `LLMBackend` instance that routes requests to the Google Gemini endpoint

#### Scenario: BackendUnavailableError raised when key is absent
- **WHEN** `GOOGLE_API_KEY` is not set
- **THEN** `create_google_backend()` SHALL raise `BackendUnavailableError`

### Requirement: Google backend is a subclass of OpenAILikeBackend
`_GoogleBackend` SHALL inherit from `OpenAILikeBackend` and implement only `_call()`.

#### Scenario: Text completion
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL return the response text as `str`

#### Scenario: Tool call response
- **WHEN** `complete(messages, tools=[...])` is called and the model requests a tool
- **THEN** it SHALL return a `ToolUse` instance
