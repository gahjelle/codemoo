## 1. Extend ToolDef with validate field

- [x] 1.1 Add `validate: Callable[..., str | None] | None = None` field to `ToolDef` in `src/codemoo/core/tools/__init__.py`
- [x] 1.2 Verify existing tools (`read_file`, `write_file`, `list_files`, `run_shell`, `reverse_string`, `get_datetime`) still construct without `validate` and that `tool.validate` is `None`

## 2. Add dispatch_tool helper and ValidationBlockEvent

- [x] 2.1 Add `ValidationBlockEvent` frozen dataclass to `src/codemoo/core/bots/commentator_bot.py` with fields `bot_name`, `tool_name`, `arguments`, `reason`
- [x] 2.2 Add `_comment_on_validation_block()` method to `CommentatorBot` with dim prefix `Blocked: <reason>` and LLM persona commentary prompt
- [x] 2.3 Extend `CommentatorBot.comment()` union type and dispatch to handle `ValidationBlockEvent`
- [x] 2.4 Add `async def dispatch_tool(tool, arguments, bot_name, commentator)` to `src/codemoo/core/tools/__init__.py`; export it in `__all__`

## 3. Update bot dispatch sites

- [x] 3.1 Replace `tool_map[response.name].fn(**response.arguments)` with `await dispatch_tool(...)` in `SingleTurnToolBot.on_message()` (`src/codemoo/core/bots/single_turn_tool_bot.py`)
- [x] 3.2 Replace `tool.fn(**response.arguments)` with `await dispatch_tool(...)` in `AgentBot.on_message()` (`src/codemoo/core/bots/agent_bot.py`)
- [x] 3.3 Replace both `tool.fn(**response.arguments)` calls (approved and non-approval branches) with `await dispatch_tool(...)` in `GuardBot.on_message()` (`src/codemoo/core/bots/guard_bot.py`)
- [x] 3.4 Replace both `tool.fn(**response.arguments)` calls with `await dispatch_tool(...)` in `ProjectBot.on_message()` (`src/codemoo/core/bots/project_bot.py`)

## 4. Session folder parameter plumbing

- [x] 4.1 Add `session_folder: Path` parameter to `make_bots()` in `src/codemoo/core/bots/__init__.py`; forward to each `_make_bot()` call
- [x] 4.2 Add `session_folder: Path` parameter to `_make_bot()`; thread it through to validator construction (no validator application yet — that's step 5)

## 5. File tool validators

- [x] 5.1 Add `make_file_validator(session_folder: Path) -> Callable` in `src/codemoo/core/tools/files.py` (or a new `src/codemoo/core/tools/sandbox.py`): resolves `path` argument with `Path.resolve()` and checks `is_relative_to(session_folder.resolve())`; returns an explicit error string naming both paths on failure
- [x] 5.2 In `_make_bot()`, apply `dataclasses.replace(tool, validate=make_file_validator(session_folder))` to `read_file`, `write_file`, and `list_files`

## 6. Shell tool validator

- [x] 6.1 Add `make_shell_validator(session_folder: Path) -> Callable` in `src/codemoo/core/tools/shell.py` (or `sandbox.py`): tokenises with `shlex.split`, checks each token (and flag values after `=`) for `/` prefix (excluding `./`) or `..` prefix; returns explicit error string on match or `shlex.ParseError`
- [x] 6.2 In `_make_bot()`, apply `dataclasses.replace(tool, validate=make_shell_validator(session_folder))` to `run_shell`

## 7. Session folder in context loading

- [x] 7.1 Add `session_folder: Path` parameter to `read_project_context()` in `src/codemoo/core/context.py`; for `source_type == "file"`, resolve path as `session_folder / source_name` instead of bare `Path(source_name)`
- [x] 7.2 Update `ProjectBot.startup()` to pass `session_folder` to `read_project_context()`; add `session_folder: Path` field to `ProjectBot`
- [x] 7.3 Pass `session_folder` into `ProjectBot` construction in `_make_bot()`

## 8. TUI entry point

- [x] 8.1 Capture `session_folder = Path.cwd()` at the top of `_setup()` (and `_chat()`) in `src/codemoo/frontends/tui.py`; pass it through `make_bots(..., session_folder=session_folder)`

## 9. Tests

- [x] 9.1 Test `dispatch_tool` with `validate=None`: result equals `fn` output
- [x] 9.2 Test `dispatch_tool` with validator returning error: `fn` not called, error returned, `ValidationBlockEvent` emitted to commentator
- [x] 9.3 Test file validator: path within session folder → `None`; `../` traversal → error string containing both paths; absolute path outside → error; absolute path inside → `None`
- [x] 9.4 Test shell validator: safe relative command → `None`; absolute path token → error; `../` token → error; `./` prefix → `None`; flag with embedded absolute path → error; unparseable command → error

## 10. Verification and documentation

- [x] 10.1 Run `uv run ruff format src/ tests/`
- [x] 10.2 Run `uv run ruff check src/ tests/`
- [x] 10.3 Run `uv run ty check src/ tests/`
- [x] 10.4 Run `uv run pytest`
- [x] 10.5 Read `AGENTS.md` and update the Tools Architecture section to mention `session_folder` sandboxing and `dispatch_tool`
