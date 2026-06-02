## Why

The current demo progression introduces GuardBot (approval gating) before RetryBot (error recovery), which inverts the natural pedagogical order: a bot should first learn to handle failure gracefully, then learn to gate dangerous operations. Swapping the two makes each step's new capability build more logically on the previous one. The swap also requires new names to preserve the letter-sequence property of the bot names.

## What Changes

- **RetryBot** moves one step earlier in the progression (position 5, directly after AgentBot). It is renamed from "Lava" to "Crow" and its emoji changes from `VOLCANO` to `BIRD`. The approval gate logic is removed; its sole new capability over AgentBot is `catch_errors=True` on all tool calls.
- **GuardBot** moves one step later (position 6, directly after RetryBot). It is renamed from "Cato" to "Lock"; its `LOCK` emoji is unchanged. It gains `catch_errors=True` on all tool calls (inheriting RetryBot's capability) in addition to its existing approval gate.
- The six bot instruction files are updated to reflect the new names.
- The `_make_bot` match statement in `bots/__init__.py` is reordered to match the new progression.
- `AGENTS.md` credo table and inline references are updated.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `retry-bot`: Position changes from after GuardBot to before GuardBot; name/emoji change; approval gate logic removed; now defined as "AgentBot + catch_errors=True".
- `guard-bot`: Position changes from before RetryBot to after RetryBot; name changes from Cato to Lock; gains `catch_errors=True` on all dispatch_tool calls.

## Non-goals

- Example prompts are not updated in this change; that is a separate planned change.
- No behaviour visible to users changes — the capabilities themselves are identical; only their order and names differ.

## Impact

- `src/codemoo/config/codemoo.toml` — progression order in `all`, `m365`, `workspace` scripts; `[bots.GuardBot]` and `[bots.RetryBot]` name/emoji fields
- `src/codemoo/core/bots/retry_bot.py` — remove approval gate logic, update docstring
- `src/codemoo/core/bots/guard_bot.py` — add `catch_errors=True`, update docstring
- `src/codemoo/core/bots/__init__.py` — reorder `GuardBot`/`RetryBot` cases in `_make_bot`
- Six instruction files in `src/codemoo/config/instructions/`
- `AGENTS.md`
