## Why

`GeneralToolBot` is a misleading name — it suggests a generic catch-all bot, but its actual role is to implement the single-turn tool-call loop that concrete subclasses build on. Renaming it to `SingleTurnToolBot` makes the contract immediately legible to anyone reading the code.

## What Changes

- Rename the class `GeneralToolBot` → `SingleTurnToolBot` in `src/codemoo/core/bots/general_tool_bot.py`
- Rename the source file `general_tool_bot.py` → `single_turn_tool_bot.py`
- Update all imports across the codebase (`change_bot.py`, `read_bot.py`, `tool_bot.py`, `send_bot.py`, `agent_bot.py`, `scan_bot.py`, and tests)
- Rename the spec directory `openspec/specs/general-tool-bot/` → `openspec/specs/single-turn-tool-bot/` and update the spec content

## Non-goals

- No behaviour changes — this is a pure rename with no functional impact.
- No changes to subclass names (`ToolBot`, `FileBot`, `ShellBot`, etc.).

## Capabilities

### New Capabilities

_(none — this is a rename, not a new capability)_

### Modified Capabilities

- `general-tool-bot`: Rename to `single-turn-tool-bot`; update class name and all textual references within the spec.

## Impact

- All files that import or reference `GeneralToolBot` / `general_tool_bot` require updates.
- The spec directory moves from `openspec/specs/general-tool-bot/` to `openspec/specs/single-turn-tool-bot/`.
- No API or protocol changes; the public surface of subclasses is unchanged.
