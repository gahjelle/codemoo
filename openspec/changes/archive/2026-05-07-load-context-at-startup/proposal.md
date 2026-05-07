## Why

ProjectBot calls `read_project_context()` on every `on_message()` invocation, re-reading a file or making a remote API call (SharePoint, Google Drive) for each user message. The context does not change during a session, so this is unnecessary I/O that slows every response and conflates startup concerns with per-message logic.

## What Changes

- **ProjectBot** no longer reads context in `on_message`. It receives a pre-loaded `context: str | None` string at construction and injects it into the system prompt directly.
- **ProjectBot** gains an `async startup()` method that loads context once, before any user interaction.
- **`make_bots`** becomes async and calls `startup()` on any bot that implements it, establishing a general bot startup protocol.
- **CommentatorBot** gains an event buffer so `comment()` can be called before `register()`. Events emitted during startup are queued and flushed to the UI when `register()` is called in `ChatApp.on_mount`.
- **`ChatApp.on_mount`** becomes async. The `commentator.register()` call moves here from `__init__`, so startup commentary appears in the TUI before user input.
- **`tui.py`** setup functions go async; cyclopts entry points use `asyncio.run()`.

## Capabilities

### New Capabilities

- `bot-startup-protocol`: A general async lifecycle hook — any bot may implement `async startup()`. `make_bots` calls it after constructing all bots, before the TUI starts. This enables any bot to perform one-time initialization (loading data, warming connections) with results visible as startup commentary.

### Modified Capabilities

- `project-context`: Requirement changes from loading context on each message to loading it once at startup. The context source configuration and injection format are unchanged.
- `commentator-bot`: `comment()` may now be called before `register()`. Events are buffered and replayed when `register()` is called, rather than requiring `register()` to be called first.

## Impact

- `src/codemoo/core/bots/project_bot.py` — field and method changes
- `src/codemoo/core/bots/commentator_bot.py` — buffering logic
- `src/codemoo/core/bots/__init__.py` — async factory
- `src/codemoo/chat/app.py` — async `on_mount`
- `src/codemoo/frontends/tui.py` — async setup functions
- No changes to config schema, `context.py`, or tool definitions

## Non-goals

- Hot-reloading context during a session (context is intentionally frozen at startup)
- Applying the startup protocol to existing bots other than ProjectBot
- Changing context source configuration format or supported source types
