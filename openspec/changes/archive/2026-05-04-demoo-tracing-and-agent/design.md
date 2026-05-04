## Context

`demoo` is a CLI frontend (`src/codemoo/frontends/cli.py`) used in live demonstrations. It currently runs single-shot LLM and tool calls but shows no output until the final answer. Audiences cannot see the HTTP endpoint, the JSON payload sent to the LLM, or the raw response — the mechanics that the demo exists to explain.

The LLM backends (`_AnthropicBackend`, `OpenAILikeBackend` subclasses) encapsulate serialization and SDK calls. The `resolve_backend()` factory constructs them from config. All Rich formatting today lives in `cli.py`.

## Goals / Non-Goals

**Goals:**
- Make every LLM request/response visible in the terminal with Rich formatting
- Show the actual serialized payload each backend sends (Anthropic vs OpenAI wire format difference)
- Add a `demoo agent` command that runs a full tool loop with per-round tracing
- Keep backends unaware of Rich; all formatting stays in the CLI layer

**Non-Goals:**
- TUI tracing
- HTTP-level wire capture (raw bytes, headers)
- Persistent log files
- Payload truncation

## Decisions

### Decision 1: Tracer protocol injected into backends (not httpx hooks)

**Chosen**: A `Tracer` protocol with two sync callbacks (`on_request(url, payload_dict)`, `on_response(response_dict)`) accepted by backend constructors. Backends call these hooks with the actual payload dict they construct before each SDK call, and with `response.model_dump()` after.

**Alternatives considered**:
- *httpx transport hook*: Would capture true wire bytes, but both SDKs apply compression/encoding that makes the captured JSON noisy. Also requires private SDK internals knowledge.
- *TracingBackend wrapper*: A decorator around `LLMBackend` that intercepts `complete()`. Cannot see the serialized payload (it lives inside the backend) and cannot see the raw response (SDK parses it before returning).
- *CLI reconstructs payload*: Duplicates each backend's serialization logic in the CLI. Fragile and inconsistent.

**Rationale**: The injected `Tracer` gives us the exact dict passed to the SDK — the closest thing to "what was sent" without going to the HTTP layer. Each backend is responsible for calling it, which is the right place: backends know their own wire format.

### Decision 2: Tracer is a dataclass with optional callbacks, not a Protocol

**Chosen**: `@dataclasses.dataclass` with `on_request: Callable[..., None] | None = None` and `on_response: Callable[..., None] | None = None`. Backends check `if self._tracer:` before calling.

**Rationale**: A dataclass with optional fields means no-op tracing is a `None` check, not a null-object pattern. Keeps backends simple. The `Tracer` type lives in `core/tracer.py` to avoid circular imports (backends import from core, not frontends).

### Decision 3: URL stored at backend construction time

Each backend stores `self._url: str` set from the SDK client's `base_url` at `__init__` time. For Anthropic: `str(client.base_url) + "messages"`. For OpenAI-like: `str(client.base_url) + "chat/completions"`. This avoids re-deriving the URL on each call.

**Rationale**: The URL is fixed per backend instance; storing it once is simpler and correct.

### Decision 4: `resolve_backend()` accepts an optional `Tracer`

`resolve_backend(config, tracer=None)` threads the tracer through `_create()` into each backend factory. All existing callers (TUI) pass no tracer and get the unmodified behavior.

**Rationale**: Single injection point. TUI is unaffected; CLI passes a `RichTracer` instance.

### Decision 5: `demoo agent` runs the tool loop inline in `cli.py`

Rather than instantiating `AgentBot`, the `agent` command implements the same `while True` loop directly, with tracing calls woven in. The loop logic is short (< 20 lines) and adding it inline avoids importing bot infrastructure into the CLI.

Tools exposed: `read_file`, `write_file`, `list_files`, `run_shell` from `TOOL_REGISTRY`.

**Rationale**: `AgentBot` was designed for the TUI chat context (takes `ChatMessage`, returns `ChatMessage`). The CLI works with plain strings and `Message` objects. Adapting `AgentBot` would require more glue than writing the loop directly.

### Decision 6: Tool call tracing lives in the `agent`/`tool` command bodies, not backends

LLM round-trip tracing (request/response) goes through the `Tracer`. Tool dispatch tracing (tool call + result) is done directly in `cli.py` because the CLI controls tool dispatch — it's not mediated by any backend abstraction.

**Rationale**: Clean separation: backends report network events, CLI reports tool events.

## Risks / Trade-offs

- **`response.model_dump()` may include SDK-internal fields** not in the actual API response. For a demo this is acceptable; audiences see a superset, not a subset.
- **Anthropic's `base_url` returns a `URL` object** (httpx type), not a plain string. Must call `str()` on it before concatenation.
- **OpenAI-like `base_url` trailing slash**: `client.base_url` for OpenAI SDKs may or may not have a trailing slash. Must normalise (e.g. `str(client.base_url).rstrip("/") + "/chat/completions"`).
- **Google backend** (`llm/google.py`) extends `OpenAILikeBackend` via Google's OpenAI-compatible endpoint — it gets tracer wiring for free alongside OpenAI, Mistral, Ollama, and OpenRouter. No separate instrumentation needed.

## Migration Plan

No config changes. No breaking changes to `LLMBackend` protocol (tracer is injected at construction, not through `complete()`). TUI calls `resolve_backend(config)` without a tracer and is unaffected.

## Open Questions

None.
