## Why

During live demos it is useful to clear a bot's conversation context mid-session — either as a quick reset after a tangent, or to let bots like Lore (ProjectBot) and Aura (MemoryBot) reload their context and memory files from disk without advancing to the next bot. No keyboard shortcut for this exists today.

## What Changes

- **Ctrl-R** shortcut in demo mode restarts the current bot in-place
- Pressing Ctrl-R mounts a static visual divider in the chat log so prior conversation is preserved but visually separated
- A new `BotRestartEvent` is fired to the commentator, which generates a persona-driven quip about the fresh start
- Conversation history (`_history`) is cleared
- Preset prompt index is reset to 0 and the DemoHeader remaining count returns to the full total
- `startup()` is re-run (via `run_worker`) so bots with project context or memory reload from disk
- "Ctrl-R: restart" hint is added to the `DemoHeader` hint line
- This shortcut is gated to demo mode only (no change to non-demo behaviour)

## Capabilities

### New Capabilities

- `demo-restart-shortcut`: Ctrl-R keyboard shortcut that resets the current demo bot session in-place, with a divider widget and commentator quip

### Modified Capabilities

- `demo-mode`: New Ctrl-R requirement added to the existing keyboard shortcut surface
- `commentary-events`: New `BotRestartEvent` added to the event union handled by `CommentatorBot`

## Impact

- `src/codemoo/chat/app.py` — `on_key` handler, new `_restart_bot()` method, new divider widget or inline label
- `src/codemoo/chat/demo_header.py` — Ctrl-R added to the hint line
- `src/codemoo/core/bots/commentator_bot.py` — `BotRestartEvent` dataclass, `_comment_on_restart()` method, updated `comment()` union type

## Non-goals

- This shortcut is not exposed in non-demo (plain chat) mode
- It does not restart the entire demo progression — Ctrl-N still handles bot-to-bot transitions
- It does not re-run init hooks (authentication) — those are already done at demo startup
