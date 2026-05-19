## Why

The `context_management` capability name is misleading — the feature only displays context statistics, it doesn't yet support editing. Renaming it to `context_display` is more accurate and leaves room for a future `context_management` that actually manipulates context. Alongside the rename, two small UX improvements are included: lifting Ctrl-R (restart) out of demo-mode so it's available in all sessions, and adding a read-only context inspector modal that lets users see exactly what items are in the current LLM context.

## What Changes

- Rename the `"context_management"` capability string to `"context_display"` in `schema.py`, `app.py`, and `codemoo.toml` (8 variant entries)
- Ctrl-R (restart): remove the demo-mode guard so it fires in any `ChatApp` session; wrap the `DemoHeader.update_prompt_state()` call in a demo-mode check to keep demo behavior intact
- New `ContextInspectModal` widget (`src/codemoo/chat/context_inspect.py`): a read-only `ModalScreen` opened by Ctrl-X when the `context_display` capability is active; lists all current `ContextItem`s as scrollable one-liners with mode glyphs, type tags, and content previews; dismissed by Escape
- `ChatApp.on_key` gains two new non-demo branches: Ctrl-R (universal restart) and Ctrl-X (context inspector, gated by `"context_display" in self._active_capabilities`)

## Non-goals

- No editing of context items — the modal is strictly read-only
- No live updates while the modal is open — snapshot is taken at open time
- No visual shortcut indicator for Ctrl-X or Ctrl-R outside demo mode (DemoHeader already shows `^R: restart`)
- No changes to `ContextStatus` widget behavior or the token estimation logic

## Capabilities

### New Capabilities

- `context-inspector`: Read-only modal that displays the current `list[ContextItem]` — mode, type, preview, pin state, and turn-group separators — opened by Ctrl-X when the `context_display` capability is active

### Modified Capabilities

- `bot-capability-declarations`: BotCapability Literal changes from `"context_management"` to `"context_display"`; the rename propagates through `_CAPABILITY_BINDERS` and all variant configs
- `demo-restart-shortcut`: Ctrl-R is no longer a no-op outside demo mode; it now performs a full session restart (clear history, re-run startup, mount divider) in any `ChatApp` session

## Impact

- `src/codemoo/config/schema.py` — BotCapability Literal
- `src/codemoo/config/codemoo.toml` — 8 variant capability entries
- `src/codemoo/chat/app.py` — `_CAPABILITY_BINDERS` key, `on_key`, `_restart_bot`
- `src/codemoo/chat/context_inspect.py` — new file
- `src/codemoo/chat/chat.tcss` — new modal CSS
