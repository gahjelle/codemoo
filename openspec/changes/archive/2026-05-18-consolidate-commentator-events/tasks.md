## 1. New Event Dataclasses

- [x] 1.1 Add `ToolEvent(outcome, bot_name, tool_name, arguments, detail=None)` frozen dataclass to `commentator_bot.py`
- [x] 1.2 Add `LoadEvent(kind, bot_name, source, path, content)` frozen dataclass to `commentator_bot.py`
- [x] 1.3 Remove `ToolCallEvent`, `ValidationBlockEvent`, and `ToolErrorEvent` dataclasses from `commentator_bot.py`

## 2. CommentatorBot Template Support

- [x] 2.1 Add `templates: dict[str, str]` constructor field to `CommentatorBot`
- [x] 2.2 Replace `_comment_on_tool_call`, `_comment_on_validation_block`, and `_comment_on_tool_error` with a single `_comment_on_tool(event: ToolEvent)` method using `self.templates[event.outcome]`
- [x] 2.3 Replace `_comment_on_context` and `_comment_on_memory` with a single `_comment_on_load(event: LoadEvent)` method using `self.templates[event.kind]`
- [x] 2.4 Update `comment()` union type to `ToolEvent | LoadEvent | BotRestartEvent` and replace the six-branch isinstance chain with three branches

## 3. Config: Template Files and Loading

- [x] 3.1 Create `src/codemoo/config/commentary_templates/` directory with five template files: `tool_call.txt`, `tool_blocked.txt`, `tool_error.txt`, `load_context.txt`, `load_memory.txt` — port existing prompt wording from `_comment_on_*` methods using `{placeholder}` syntax
- [x] 3.2 Add `[commentary_templates]` section to `codemoo.toml` mapping each key to its filename (e.g. `call = "tool_call.txt"`)
- [x] 3.3 Add `commentary_templates: dict[str, str]` field to `CodemooConfig` in `schema.py`
- [x] 3.4 Add `_resolve_commentary_template_refs()` to `config/__init__.py` (mirrors `_resolve_commentator_refs`) and call it from `_resolve_file_refs()`
- [x] 3.5 Pass `config.commentary_templates` as `templates=` when constructing `CommentatorBot` in the TUI and any other construction sites

## 4. dispatch_tool: Unified Emission

- [x] 4.1 Update `dispatch_tool` in `core/tools/__init__.py` to import and emit `ToolEvent` for all three outcomes: emit `ToolEvent(outcome="blocked")` on validation failure, `ToolEvent(outcome="call")` after validation passes (before `tool.fn()`), and `ToolEvent(outcome="error")` when the result starts with `"Error "`
- [x] 4.2 Remove the lazy local imports of `ValidationBlockEvent` and `ToolErrorEvent` from `dispatch_tool`

## 5. context.py: LoadEvent Migration

- [x] 5.1 Replace `ContextLoadEvent` with `LoadEvent(kind="context")` in `read_project_context()` in `core/context.py`
- [x] 5.2 Replace `MemoryLoadEvent` with `LoadEvent(kind="memory")` in `read_memory_file()` in `core/context.py`
- [x] 5.3 Remove `ContextLoadEvent` and `MemoryLoadEvent` dataclasses from `core/context.py`

## 6. Bot Cleanup: Remove Explicit ToolCallEvent Emission

- [x] 6.1 Remove `await commentator.comment(ToolCallEvent(...))` and the `ToolCallEvent` import from `single_turn_tool_bot.py`
- [x] 6.2 Remove the same from `agent_bot.py`
- [x] 6.3 Remove the same from `guard_bot.py`
- [x] 6.4 Remove the same from `project_bot.py`
- [x] 6.5 Remove the same from `retry_bot.py`

## 7. Tests

- [x] 7.1 Update any tests that construct or assert on `ToolCallEvent`, `ValidationBlockEvent`, `ToolErrorEvent`, `ContextLoadEvent`, or `MemoryLoadEvent` to use `ToolEvent` and `LoadEvent`
- [x] 7.2 Add or update tests for `dispatch_tool` to verify `ToolEvent(outcome="call")` is emitted after validation passes, `ToolEvent(outcome="blocked")` on validation failure, and no double-emission when blocked
- [x] 7.3 Add or update tests for `CommentatorBot.comment()` to verify it dispatches correctly for `ToolEvent` (all three outcomes) and `LoadEvent` (both kinds) using the template dict

## 8. Documentation and Verification

- [x] 8.1 Review `AGENTS.md` and update the Commentary Events section to reflect the new event types and dispatch_tool-centric emission
- [x] 8.2 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 8.3 Run `uv run ty check src/ tests/`
- [x] 8.4 Run `uv run pytest` and confirm all tests pass
