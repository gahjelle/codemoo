## Why

The demo progression lacks a visible "before" moment for error handling: all bots already return tool errors as strings, so the LLM always gets to reason about them. Making early bots raise on tool errors (instead of feeding them to the LLM) creates a clear contrast — and gives RetryBot a concrete, demonstrable capability: catching those errors and turning them into data.

## What Changes

- **Bug fix**: `dispatch_tool` was checking for `"Error "` (no colon) but all tool error strings use `"Error: "` — the error commentary event never fired.
- **`catch_errors` parameter**: `dispatch_tool` gains `catch_errors: bool = False`. When `False` (default), a tool result starting with `"Error: "` raises `ToolError` instead of returning. When `True`, the error commentary fires and the string is returned to the LLM. Commentary is suppressed on the raise path to avoid double-reporting with ErrorBot.
- **Exception hierarchy**: New `src/codemoo/core/exceptions.py` introduces `CodemooError` (base), `BackendUnavailableError` (moved from `llm/exceptions.py`), and `ToolError` (new). `llm/exceptions.py` is deleted.
- **RetryBot behavior**: **BREAKING** — retry-counting logic removed entirely (`retry_counts`, `_RETRY_BUDGET`, `_escalation_message`). RetryBot's new defining capability is passing `catch_errors=True` to `dispatch_tool`. CompactBot loses retry-counting for the same reason.
- **Bot progression reorder**: RetryBot moves from after MemoryBot to between GuardBot and ProjectBot across all progressions (code, M365, Workspace).
- **Bot renames**:
  - RetryBot: `Undo` → `Lava`, `GAME DIE` → `VOLCANO`
  - ProjectBot: `Lore` → `Aria`, `OPEN BOOK` → `MICROPHONE`
  - MemoryBot: `Aura` → `Ursa`, `SMILING FACE WITH HALO` → `BEAR FACE`

## Non-goals

- Updating example prompts for Rune (ReadBot) through Cato (GuardBot) — these will need revisiting since errors now raise in those bots, but that is a separate follow-up change.
- Changing how `run_shell` formats errors — already updated separately.
- Modifying any bot's system prompt text.

## Capabilities

### New Capabilities

- `tool-error-raise`: `dispatch_tool` raises `ToolError` on error results when `catch_errors=False`; commentary suppressed on raise path.
- `codemoo-exception-hierarchy`: `CodemooError` base class with `BackendUnavailableError` and `ToolError` subclasses in `core/exceptions.py`.

### Modified Capabilities

- `retry-bot`: Behavior changes from retry-counting to error-catching (`catch_errors=True`). New name, emoji, and position in progression.
- `tool-error-commentary`: Commentary now only fires when `catch_errors=True`; bug fix for `"Error: "` prefix check.

## Impact

- `src/codemoo/core/tools/__init__.py` — `dispatch_tool` signature change
- `src/codemoo/core/exceptions.py` — new file
- `src/codemoo/llm/exceptions.py` — deleted
- `src/codemoo/llm/` — 6 import sites updated (google, ollama, mistral, openrouter, openai, anthropic, factory)
- `src/codemoo/core/bots/retry_bot.py` — retry logic removed, `catch_errors=True` added
- `src/codemoo/core/bots/compact_bot.py` — retry logic removed
- `src/codemoo/config/codemoo.toml` — bot names, emojis, and progression order updated
- All bots that call `dispatch_tool` implicitly get the new raise behavior with no code changes required (the default `catch_errors=False` is the breaking default)
