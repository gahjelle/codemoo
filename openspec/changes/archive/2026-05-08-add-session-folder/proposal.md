## Why

Codemoo's file and shell tools currently operate with no scope boundary — an agent can read `/etc/passwd`, traverse `../` out of the working directory, or run shell commands referencing arbitrary absolute paths. Formalising the working directory as a **session folder** establishes a clear boundary for tool execution and lays the groundwork for per-project history and settings.

## What Changes

- `ToolDef` gains an optional `validate` field: a callable checked before `fn` is invoked; a non-`None` return hard-blocks the call and feeds an error to the LLM.
- A new async `dispatch_tool()` helper replaces direct `tool.fn()` calls in all bots; it runs `validate`, emits a `ValidationBlockEvent` if blocked, then calls `fn`.
- `read_file`, `write_file`, `list_files`, and `run_shell` are wrapped at bot construction with session-folder validators; the underlying tool definitions stay pure.
- `run_shell` shell scanning: `shlex.split()` tokenises the command; tokens starting with `/` or `..` (excluding `./`) trigger a hard block. `shlex.ParseError` also hard-blocks (fail closed).
- File path validation resolves the argument with `Path.resolve()` and checks `is_relative_to(session_folder.resolve())`.
- A new `ValidationBlockEvent` is added alongside `ToolCallEvent`; the `CommentatorBot` generates colour commentary for blocked calls, with a dim factual prefix line.
- Session folder (`Path.cwd()` at startup) flows as an explicit parameter through `make_bots()` → `_make_bot()`; it is not a global singleton.
- `context.py` file-based AGENTS.md lookup is anchored to the session folder.

## Non-goals

- A `--path` CLI option to override the session folder (deferred).
- Session history or per-project settings storage (deferred; session folder is the prerequisite).
- Sandboxing network calls or environment variable access.
- Whitelisting specific absolute paths (e.g. `/tmp`); all paths outside the session folder are blocked.

## Capabilities

### New Capabilities

- `session-folder`: The session folder concept — `Path.cwd()` at startup, passed explicitly through the bot construction chain; used as the root for tool sandboxing and context file lookup.
- `tool-sandbox`: Validation layer for tools — `validate` field on `ToolDef`, `dispatch_tool()` helper, session-folder-aware validators for file and shell tools, hard-block semantics.

### Modified Capabilities

- `structured-tool-def`: Adds optional `validate: Callable[..., str | None] | None` field.
- `commentary-events`: Adds `ValidationBlockEvent` (bot_name, tool_name, arguments, reason); `CommentatorBot.comment()` union type and `_comment_on_validation_block()` handler.
- `project-context`: File-based context lookup (`AGENTS.md`) is resolved relative to the session folder rather than bare `Path(name)`.

## Impact

- **`src/codemoo/core/tools/__init__.py`**: `ToolDef` gains `validate`; new `dispatch_tool()` async helper exported.
- **`src/codemoo/core/tools/files.py`**, **`shell.py`**: No changes — validators applied externally at bot construction.
- **`src/codemoo/core/bots/__init__.py`**: `_make_bot()` and `make_bots()` accept `session_folder: Path`; file/shell tools wrapped with validators.
- **`src/codemoo/core/bots/single_turn_tool_bot.py`**, **`agent_bot.py`**, **`guard_bot.py`**, **`project_bot.py`**: Single-line change each — `tool.fn(**args)` → `await dispatch_tool(...)`.
- **`src/codemoo/core/bots/commentator_bot.py`**: New `ValidationBlockEvent` dataclass; `comment()` dispatch extended.
- **`src/codemoo/core/context.py`**: `read_project_context()` accepts `session_folder: Path`; file lookup uses it.
- **`src/codemoo/frontends/tui.py`**: Captures `Path.cwd()` at entry and passes through `make_bots()`.
- No new dependencies; no changes to LLM backends, config schema, or TUI widgets.
