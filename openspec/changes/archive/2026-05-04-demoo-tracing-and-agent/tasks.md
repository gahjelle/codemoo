## 1. Tracer Protocol

- [x] 1.1 Create `src/codemoo/core/tracer.py` with `Tracer` dataclass: two optional `Callable` fields `on_request` and `on_response`, both defaulting to `None`

## 2. Anthropic Backend Instrumentation

- [x] 2.1 Add `tracer: Tracer | None = None` to `_AnthropicBackend.__init__`; store as `self._tracer` and derive `self._url = str(client.base_url) + "messages"`
- [x] 2.2 In `_AnthropicBackend.complete()`, build an explicit `payload` dict (`model`, `max_tokens`, `system`, `messages`, `tools`) before the SDK call
- [x] 2.3 Call `self._tracer.on_request(self._url, payload)` before `client.messages.create()` and `self._tracer.on_response(response.model_dump())` after (both guarded by `if self._tracer`)
- [x] 2.4 Update `create_anthropic_backend(model, tracer=None)` to accept and pass through the tracer

## 3. OpenAI-like Backend Instrumentation

- [x] 3.1 Add `tracer: Tracer | None = None` and `url: str = ""` parameters to `OpenAILikeBackend.__init__`; store both on `self`
- [x] 3.2 In `OpenAILikeBackend.complete()`, build explicit `payload` dict (`model`, `messages`, optionally `tools`) before calling `_call()`
- [x] 3.3 Call `self._tracer.on_request(self._url, payload)` before `_call()` and `self._tracer.on_response(response.model_dump())` after (guarded by `if self._tracer`)
- [x] 3.4 Update each OpenAI-like factory (`create_openai_backend`, `create_mistral_backend`, `create_openrouter_backend`, `create_ollama_backend`) to accept `tracer=None` and pass `tracer` + derived `url` to the backend constructor
- [x] 3.5 Derive URL in each factory: `str(client.base_url).rstrip("/") + "/chat/completions"`

## 4. Factory Wiring

- [x] 4.1 Add `tracer: Tracer | None = None` to `resolve_backend(config, tracer=None)` in `llm/factory.py`
- [x] 4.2 Thread `tracer` through `_create(name, model, base_url, tracer=None)` to each `create_*_backend()` call

## 5. RichTracer and demoo llm Command

- [x] 5.1 Implement `make_rich_tracer(console: Console) -> Tracer` in `frontends/cli.py` — `on_request` prints a "Request" rule, URL in cyan, payload as `Syntax("json")`; `on_response` prints a "Response" rule and response as `Syntax("json")`
- [x] 5.2 Update `demoo llm` to call `resolve_backend(config, tracer=make_rich_tracer(stdout))` and add a "Reply" `console.rule()` before printing the markdown

## 6. Enhanced demoo tool Command

- [x] 6.1 Update `demoo tool` signature to `tool(query: str, *, system: str = "You are a helpful assistant with access to file tools.")` and pass `tracer=make_rich_tracer(stdout)` to `resolve_backend()`
- [x] 6.2 Prepend `Message(role="system", content=system)` as the first message in the context
- [x] 6.3 Replace the existing `[dim]tool call: ...[/dim]` print with a "Tool Call" `console.rule()` showing tool name, call ID, and arguments as formatted JSON
- [x] 6.4 Add a "Tool Result" `console.rule()` showing the call ID and tool output after executing the tool
- [x] 6.5 Add a "Reply" `console.rule()` before the final markdown print

## 7. New demoo agent Command

- [x] 7.1 Add `async def agent(query: str, *, system: str = "You are a helpful assistant with access to file and shell tools.") -> None` command to `cli.py` with cyclopts `@app.command`
- [x] 7.2 Look up tools `["read_file", "write_file", "list_files", "run_shell"]` from `TOOL_REGISTRY`; build `tool_map`
- [x] 7.3 Initialize `messages` with `Message(role="system", content=system)` and the user query
- [x] 7.4 Implement the `while True` loop: call `llm.complete(messages, tools)`, break on plain string, else execute tool and extend `messages`
- [x] 7.5 Add round counter; prefix each `console.rule()` with `f"Round {n} · "` for request, response, tool call, and tool result sections
- [x] 7.6 Print "Tool Call" section (tool name, call ID, arguments JSON) and "Tool Result" section (call ID, output) inside the loop when a `ToolUse` is returned
- [x] 7.7 Print "Reply" `console.rule()` and markdown-rendered final answer after the loop exits

## 8. Verification

- [x] 8.1 Run `uv run ruff format src/ tests/`
- [x] 8.2 Run `uv run ruff check src/ tests/`
- [x] 8.3 Run `uv run ty check src/ tests/`
- [x] 8.4 Run `uv run pytest`
- [x] 8.5 Smoke-test `demoo llm "What is 2+2?"` and verify Request / Response / Reply sections appear
- [x] 8.6 Smoke-test `demoo tool "Read demo/greeter.py and summarise it"` and verify Tool Call / Tool Result sections appear
- [x] 8.7 Smoke-test `demoo agent "List the files in demo/ then read greeter.py"` and verify round-numbered sections appear
- [x] 8.8 Smoke-test `--system` override on both `tool` and `agent` — verify the custom system prompt appears in the traced request payload

## 9. Documentation

- [x] 9.1 Read `AGENTS.md` and update if it describes the `demoo` CLI or its commands
