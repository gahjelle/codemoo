## Why

The current commentator event system has two structural problems. First, bots emit `ToolCallEvent` immediately before calling `dispatch_tool`, while `dispatch_tool` independently emits `ValidationBlockEvent` and `ToolErrorEvent` — this means a blocked tool call produces two commentator events ("X is calling Y" then "Blocked: Z"). Second, the prompt templates that guide the LLM commentary for each event type are hardcoded Python strings inside `CommentatorBot`, making every new event type a Python code change rather than a configuration change.

## What Changes

- **Consolidate 6 event types into 3**: `ToolCallEvent`, `ValidationBlockEvent`, and `ToolErrorEvent` → `ToolEvent(outcome)` with a `Literal["call", "blocked", "error"]` discriminator; `ContextLoadEvent` and `MemoryLoadEvent` → `LoadEvent(kind)` with a `Literal["context", "memory"]` discriminator; `BotRestartEvent` unchanged.
- **Move all tool event emission into `dispatch_tool`**: Remove `commentator.comment(ToolCallEvent(...))` from all five bots (`SingleTurnToolBot`, `AgentBot`, `GuardBot`, `ProjectBot`, `RetryBot`). `dispatch_tool` emits `ToolEvent(outcome="call")` after validation passes, `ToolEvent(outcome="blocked")` instead of continuing on validation failure, and `ToolEvent(outcome="error")` on error results.
- **BREAKING**: `ToolCallEvent`, `ValidationBlockEvent`, `ToolErrorEvent`, `ContextLoadEvent`, `MemoryLoadEvent` are removed. Any code importing them must switch to `ToolEvent` and `LoadEvent`.
- **Move prompt templates to config text files**: Add a `[commentary_templates]` section to `codemoo.toml` mapping each event kind to a template file in `src/codemoo/config/commentary_templates/`. Templates use `str.format()` placeholders (`{bot_name}`, `{tool_name}`, `{sig}`, `{detail}`, `{source}`, `{path}`, `{content_len}`, `{preview}`). `CommentatorBot` loads templates at startup via the same `_resolve_*` pattern used for persona instructions.

## Non-goals

- Changing what the commentator says (persona voice, tone, or style).
- Adding new event types or new template variables in this change.
- Modifying the `BotRestartEvent` — it stays as-is.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `commentary-events`: Replace the five existing event types with `ToolEvent` and `LoadEvent`; move emission of all tool events into `dispatch_tool`; remove bot-side emission of `ToolCallEvent`.
- `commentator-bot`: Add template loading from config files; replace the hardcoded f-string prompt methods with template interpolation.
- `tool-error-commentary`: Fold into the updated `commentary-events` spec — `ToolErrorEvent` is replaced by `ToolEvent(outcome="error")` emitted from `dispatch_tool`.

## Impact

- `src/codemoo/core/bots/commentator_bot.py` — new `ToolEvent`, `LoadEvent` dataclasses; remove old event dataclasses; template loading.
- `src/codemoo/core/context.py` — update `ContextLoadEvent` → `LoadEvent(kind="context")`, `MemoryLoadEvent` → `LoadEvent(kind="memory")`.
- `src/codemoo/core/tools/__init__.py` — `dispatch_tool` emits `ToolEvent` for all three outcomes.
- `src/codemoo/core/bots/single_turn_tool_bot.py`, `agent_bot.py`, `guard_bot.py`, `project_bot.py`, `retry_bot.py` — remove `ToolCallEvent` import and explicit `commentator.comment(...)` call before `dispatch_tool`.
- `src/codemoo/config/codemoo.toml` — add `[commentary_templates]` section.
- `src/codemoo/config/commentary_templates/` — new directory with five template files: `tool_call.txt`, `tool_blocked.txt`, `tool_error.txt`, `load_context.txt`, `load_memory.txt`.
- Tests covering `commentary-events` and `tool-error-commentary` specs need updating.
