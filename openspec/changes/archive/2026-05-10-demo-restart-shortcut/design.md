## Context

The demo TUI already handles three keyboard shortcuts in `ChatApp.on_key`: Ctrl-N (next bot), Ctrl-E (insert example prompt), Ctrl-S (reopen slide). All three are gated by `if self._demo_context is None: return`, making demo-only extension straightforward.

Bots that have startup side-effects — `ProjectBot` (Lore) and `MemoryBot` (Aura) — load context and memory in a `startup()` method called once at `on_mount` via `run_worker`. Re-calling `startup()` re-reads the files from disk and reassigns `self.context` / `self.memory`, making it safe to call again. All other bots have no `startup()`.

`ChatApp._history` is the authoritative conversation history. Bots are stateless — they receive history as a parameter on every `on_message` call. Clearing `_history` is therefore sufficient to reset conversation context.

The commentator already handles four event types with the same pattern: emit a frozen dataclass, pick a persona, call LLM, post bubble. Adding a fifth is mechanical.

## Goals / Non-Goals

**Goals:**
- Add Ctrl-R shortcut visible only in demo mode
- Mount an instant static divider in the log (no async wait)
- Fire `BotRestartEvent` to the commentator for a persona quip
- Clear `_history` and reset `_prompt_index`
- Re-run `startup()` so Lore and Aura reload context/memory from disk
- Add "Ctrl-R: restart" to `DemoHeader` hint line

**Non-Goals:**
- Exposing the shortcut outside demo mode
- Re-running init hooks (OAuth/auth already done at demo startup)
- Providing a confirmation dialog before restart

## Decisions

### Divider as an inline Label in app.py (not a new widget file)

The divider is a one-off static element used only in `_restart_bot`. Creating a dedicated widget class would be over-engineering. A plain `Label` with a descriptive CSS class (`restart-divider`) is enough. The visual styling (color, padding, rule characters) goes in `chat.tcss`. This keeps `bubble.py` focused on chat messages.

**Alternative considered:** Adding a `RestartDivider` class to `bubble.py`. Rejected — `bubble.py` is for conversation bubbles, not structural separators.

### BotRestartEvent defined in commentator_bot.py

All other event dataclasses (`ToolCallEvent`, `ValidationBlockEvent`) live in `commentator_bot.py`. `ContextLoadEvent` and `MemoryLoadEvent` live in `context.py` because they originate there. `BotRestartEvent` originates in `ChatApp`, not in a bot or context loader — but placing it in `commentator_bot.py` keeps the event union in one file and avoids a new import in `app.py` for a single type. The commentator handles the event; it makes sense to co-locate the type there.

**Alternative considered:** `core/events.py` or `chat/events.py`. Rejected — small additional module for one type adds navigation overhead.

### re-run startup() via run_worker

`startup()` is an async method. `_restart_bot` is called from `on_key`, which is synchronous. The existing pattern in `on_mount` is `self.run_worker(self._run_startup())`. Using the same pattern for restart means the divider and commentator event fire synchronously (immediate), while the context/memory reload runs in the background. This is the correct order: the audience sees the reset indicator before the reload commentary appears.

### Commentator event fires before startup() re-runs

Firing `BotRestartEvent` first gives an immediate persona reaction to the restart action. The subsequent `ContextLoadEvent`/`MemoryLoadEvent` from `startup()` then narrate the reload. This produces a natural three-beat sequence: divider → "fresh start" quip → "loading context" quip.

## Risks / Trade-offs

- **Double startup() calls**: If the user hits Ctrl-R while a slow `startup()` is still running (rare), two overlapping reloads could race on `bot.context`. Mitigation: Textual workers run sequentially by default (exclusive=True is the default for `run_worker`). Verify `_run_startup` worker exclusivity at implementation time.
- **Divider visible after bot advances**: The divider is visual-only in the log. When the user presses Ctrl-N, the entire `ChatApp` is replaced, so the divider disappears naturally.
- **Header line length**: Adding "Ctrl-R: restart" may make the `DemoHeader` line too long on narrow terminals. Agreed to address as a follow-up if needed (possibly shortening the bot position label or prompt count display).
