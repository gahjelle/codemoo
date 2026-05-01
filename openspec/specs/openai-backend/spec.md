# Spec: openai-backend

## Purpose

TBD — Defines the OpenAI backend factory and its concrete `_OpenAIBackend` class, enabling Codemoo to use the OpenAI API (and compatible endpoints such as Azure AI Foundry) as an LLM backend.

## Requirements

### Requirement: OpenAI backend uses OPENAI_API_KEY
The system SHALL provide a `create_openai_backend(model: str, base_url: str | None)` factory in `llm/openai.py` that reads `OPENAI_API_KEY` from the environment and raises `BackendUnavailableError` if it is absent. When `base_url` is `None` the SDK default endpoint is used.

#### Scenario: Backend created when key is present
- **WHEN** `OPENAI_API_KEY` is set and `create_openai_backend(model, base_url=None)` is called
- **THEN** it SHALL return an `LLMBackend` instance using the standard OpenAI endpoint

#### Scenario: BackendUnavailableError raised when key is absent
- **WHEN** `OPENAI_API_KEY` is not set
- **THEN** `create_openai_backend()` SHALL raise `BackendUnavailableError`

#### Scenario: Custom base_url overrides the default endpoint
- **WHEN** `create_openai_backend(model, base_url="https://my-project.inference.ai.azure.com/v1")` is called with a key present
- **THEN** the backend SHALL send requests to the provided URL, enabling Azure AI Foundry and other OpenAI-compatible endpoints

### Requirement: OpenAI backend is a subclass of OpenAILikeBackend
`_OpenAIBackend` SHALL inherit from `OpenAILikeBackend` and implement only `_call()`, delegating all serialization and response parsing to the base class.

#### Scenario: Text completion
- **WHEN** `complete(messages, tools=None)` is called
- **THEN** it SHALL return the response text as `str`

#### Scenario: Tool call response
- **WHEN** `complete(messages, tools=[...])` is called and the model requests a tool
- **THEN** it SHALL return a `ToolUse` instance
