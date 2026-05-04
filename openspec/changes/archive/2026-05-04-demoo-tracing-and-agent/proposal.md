## Why

The `demoo` CLI is used in live demonstrations to show how LLMs and tool-calling work, but its output currently hides everything interesting: the HTTP endpoint, the JSON payload, and the raw API response. Adding request/response tracing makes the wire protocol visible to audiences and demonstrates the concrete differences between Anthropic and OpenAI-like backends. A new `agent` command rounds out the demo by showing a full agentic tool loop.

## What Changes

- **New tracing output** for all `demoo` commands: each LLM call prints the endpoint URL, the full JSON request payload, and the full JSON response, delimited by labeled `console.rule()` separators with Rich syntax highlighting.
- **New `demoo agent` command**: runs a proper tool loop (like `AgentBot`) — calls the LLM repeatedly until it returns plain text, executing tools between turns. Traces both LLM round-trips and tool calls/results, labeled by round number.
- **Enhanced `demoo tool` tracing**: the single-turn tool call now shows Request → Response (tool call) → Tool Call block → Tool Result block → Request 2 → Response 2 → Reply.
- **New `Tracer` protocol** in `codemoo.core`: two sync callbacks (`on_request`, `on_response`) injected into backends at construction time. Keeps all Rich formatting in the CLI layer.
- **Backend instrumentation**: `_AnthropicBackend` and `OpenAILikeBackend` build an explicit payload dict and call tracer hooks around the SDK call, also surfacing the endpoint URL.

## Capabilities

### New Capabilities

- `demoo-llm-tracing`: Visible request/response tracing for the `demoo llm` command — endpoint URL, JSON payload, JSON response, and final reply.
- `demoo-tool-tracing`: Extended tracing for `demoo tool` that includes tool call and tool result sections with call IDs.
- `demoo-agent-command`: A new `demoo agent` command that runs a full agentic tool loop with per-round tracing of LLM calls and tool dispatch.
- `llm-tracer`: A `Tracer` protocol and injection mechanism threading observability callbacks through `resolve_backend()` into each LLM backend.

### Modified Capabilities

- `llm-backend`: Backends now accept an optional `Tracer` and build an explicit payload dict before the SDK call.
- `multi-backend`: `resolve_backend()` threads an optional `Tracer` through to each backend constructor.

## Non-goals

- Tracing in the TUI frontend — this is CLI-only.
- HTTP-level wire capture (raw bytes, headers) — reconstructed payload dicts are sufficient for demo purposes.
- Truncation or filtering of large payloads — full output for now.
- Persistent log files — output is console-only.

## Impact

- `src/codemoo/core/tracer.py` — new file
- `src/codemoo/llm/anthropic.py` — accept and call `Tracer`
- `src/codemoo/llm/openai_like.py` — accept and call `Tracer`
- `src/codemoo/llm/factory.py` — thread `Tracer` through `resolve_backend()` / `_create()`
- `src/codemoo/frontends/cli.py` — `RichTracer`, enhanced `llm`/`tool`, new `agent` command
- No new dependencies (Rich already in project)
