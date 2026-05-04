## MODIFIED Requirements

### Requirement: LLMBackend protocol defines a single async complete method
The system SHALL define an `LLMBackend` structural protocol in `core/backend.py` with a single async method `complete(messages: list[Message], tools: list[ToolDef] | None = None) -> str | ToolUse`. Any object implementing this interface SHALL be usable as a backend without explicit subclassing. This replaces the previous dual-method approach with `complete()` and `complete_step()`.

The `Tracer` SHALL NOT appear in the `LLMBackend` protocol — it is an implementation detail of each concrete backend class, injected at construction time rather than per-call. The protocol surface is unchanged.

#### Scenario: Protocol is satisfied by any matching implementation
- **WHEN** an object exposes an async `complete(messages: list[Message], tools: list[ToolDef] | None = None) -> str | ToolUse` method
- **THEN** it SHALL satisfy the `LLMBackend` protocol

#### Scenario: Unified method handles both text and tool completion
- **WHEN** `complete(messages)` is called without tools parameter
- **THEN** it SHALL behave as text-only completion
- **WHEN** `complete(messages, tools=[...])` is called
- **THEN** it SHALL handle tool-aware completion and return either `str` or `ToolUse`

## ADDED Requirements

### Requirement: Anthropic backend accepts an optional Tracer and stores endpoint URL
`_AnthropicBackend.__init__` SHALL accept an optional `tracer: Tracer | None = None` parameter and store it as `self._tracer`. It SHALL also derive and store `self._url: str` from the SDK client's `base_url` at construction time (e.g. `str(client.base_url) + "messages"`).

#### Scenario: Anthropic backend calls tracer before and after SDK call
- **WHEN** `complete()` is called on an `_AnthropicBackend` with a non-None `tracer`
- **THEN** `tracer.on_request(self._url, payload_dict)` SHALL be called with the full payload dict before `client.messages.create()`
- **AND** `tracer.on_response(response.model_dump())` SHALL be called immediately after

#### Scenario: Anthropic payload dict shows system separate from messages
- **WHEN** `on_request` is called on an Anthropic backend
- **THEN** the payload dict SHALL have a top-level `"system"` key and a `"messages"` key (without system in the messages list), matching the Anthropic wire format

#### Scenario: No tracer means no tracing calls (no-op)
- **WHEN** `_AnthropicBackend` is constructed without a tracer (or with `tracer=None`)
- **THEN** `complete()` SHALL behave identically to the previous implementation with no additional output

### Requirement: OpenAI-like backends accept an optional Tracer and store endpoint URL
`OpenAILikeBackend.__init__` SHALL accept `tracer: Tracer | None = None` and `url: str = ""` parameters. The `url` SHALL be set by each subclass factory (e.g. `str(client.base_url).rstrip("/") + "/chat/completions"`). Before calling `_call()`, `complete()` SHALL invoke `tracer.on_request(self._url, payload_dict)` where `payload_dict` includes `model`, `messages`, and optionally `tools`. After `_call()` returns, it SHALL invoke `tracer.on_response(response.model_dump())`.

#### Scenario: OpenAI-like payload shows system folded into messages list
- **WHEN** `on_request` is called on an OpenAI-like backend with a system message
- **THEN** the payload dict SHALL have a `"messages"` key containing all messages including the one with `"role": "system"`, matching the OpenAI wire format (no top-level `"system"` key)

#### Scenario: Ollama backend URL points to local server
- **WHEN** an Ollama backend is constructed with `base_url = "http://localhost:11434/v1"`
- **THEN** `self._url` SHALL be `"http://localhost:11434/v1/chat/completions"`
