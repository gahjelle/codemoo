## 1. Dependencies

- [x] 1.1 Run `uv add anthropic openai` to add new dependencies

## 2. Restructure ToolDef

- [x] 2.1 Add `ToolParam` dataclass to `core/tools/__init__.py` (fields: `name`, `description`, `type="string"`, `required=True`)
- [x] 2.2 Replace `ToolDef.schema: dict` with `name: str`, `description: str`, `parameters: list[ToolParam]` fields
- [x] 2.3 Rewrite `read_file` tool definition using `ToolDef` + `ToolParam`
- [x] 2.4 Rewrite `write_file` tool definition using `ToolDef` + `ToolParam`
- [x] 2.5 Rewrite `reverse_string` tool definition using `ToolDef` + `ToolParam`
- [x] 2.6 Rewrite `run_shell` tool definition using `ToolDef` + `ToolParam`
- [x] 2.7 Update `__all__` in `core/tools/__init__.py` to export `ToolParam`

## 3. Update ToolDef callers in core and chat

- [x] 3.1 Remove `_tool_name()` from `core/bots/general_tool_bot.py`; replace all usages with `tool.name`
- [x] 3.2 Remove `_tool_name()` from `core/bots/agent_bot.py`; replace all usages with `tool.name`
- [x] 3.3 Update `chat/slides.py` to use `tool.name` instead of `tool.schema.get("function", {}).get("name", "")`

## 4. Mistral backend module

- [x] 4.1 Create `llm/mistral.py`: move `_MistralBackend` and `_serialize` from `llm/backend.py`
- [x] 4.2 Add `_tool_schema(tool: ToolDef) -> dict` to `llm/mistral.py` (OpenAI function-calling shape)
- [x] 4.3 Update `_MistralBackend.complete_step` to use `_tool_schema` instead of `tool.schema`
- [x] 4.4 Rename `ValueError` to `BackendUnavailableError` in `create_mistral_backend`
- [x] 4.5 Delete `llm/backend.py`

## 5. BackendUnavailableError and factory

- [x] 5.1 Create `llm/factory.py` with `BackendUnavailableError` exception class
- [x] 5.2 Add `BackendInfo(name: str, model: str)` frozen dataclass to `llm/factory.py`
- [x] 5.3 Implement `resolve_backend(config) -> tuple[ToolLLMBackend, BackendInfo]` with primary + fallback loop

## 6. Anthropic backend

- [x] 6.1 Create `llm/anthropic.py` with `_AnthropicBackend` class implementing `ToolLLMBackend`
- [x] 6.2 Implement `_serialize` for Anthropic (extract system message as separate param; handle tool result content)
- [x] 6.3 Implement `_tool_schema(tool: ToolDef) -> dict` for Anthropic (`input_schema` shape)
- [x] 6.4 Implement `complete` and `complete_step` using `anthropic.AsyncAnthropic`
- [x] 6.5 Add `create_anthropic_backend(model: str) -> ToolLLMBackend` raising `BackendUnavailableError` on missing `ANTHROPIC_API_KEY`

## 7. OpenRouter backend

- [x] 7.1 Create `llm/openrouter.py` with `_OpenRouterBackend` class implementing `ToolLLMBackend`
- [x] 7.2 Implement `_tool_schema(tool: ToolDef) -> dict` for OpenRouter (same OpenAI function-calling shape as Mistral)
- [x] 7.3 Implement `complete` and `complete_step` using `openai.AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)`
- [x] 7.4 Add `create_openrouter_backend(model: str) -> ToolLLMBackend` raising `BackendUnavailableError` on missing `OPENROUTER_API_KEY`

## 8. Config schema and TOML

- [x] 8.1 Update `ModelBackend` in `config/schema.py` to `Literal["mistral", "anthropic", "openrouter"]`
- [x] 8.2 Add `[models.backends.anthropic]` entry to `configs/codemoo.toml` with `model_name = "claude-haiku-4-5-20251001"`
- [x] 8.3 Add `[models.backends.openrouter]` entry to `configs/codemoo.toml` with `model_name = "z-ai/glm-4.5-air:free"`

## 9. Update frontends

- [x] 9.1 Replace all `create_mistral_backend(...)` calls in `frontends/tui.py` with `resolve_backend(config)`
- [x] 9.2 Replace all `create_mistral_backend(...)` calls in `frontends/cli.py` with `resolve_backend(config)`
- [x] 9.3 Update `_setup()` in `tui.py` to unpack and return `BackendInfo` from `resolve_backend`
- [x] 9.4 Update `_SetupResult` type alias in `tui.py` to include `BackendInfo`

## 10. BackendStatus widget

- [x] 10.1 Create `chat/backend_status.py` with `BackendStatus(Label)` widget; `DEFAULT_CSS` sets `height: 1`
- [x] 10.2 Add `BackendStatus` visual styles to `chat/chat.tcss` (color, padding)
- [x] 10.3 Add `backend_info: BackendInfo` parameter to `ChatApp.__init__`
- [x] 10.4 Yield `BackendStatus(backend_info)` last in `ChatApp.compose()`
- [x] 10.5 Pass `BackendInfo` from `_setup()` into all `ChatApp(...)` call sites in `tui.py`

## 11. Verification

- [x] 11.1 Run `uv run ruff check .` and fix any issues
- [x] 11.2 Run `uv run ruff format .`
- [x] 11.3 Run `uv run ty check .` and fix any type errors
- [x] 11.4 Run `uv run pytest` and ensure all tests pass
- [x] 11.5 Smoke-test the TUI: verify `BackendStatus` appears and shows correct backend/model
