## Context

Demo sessions use `ChatApp` in demo mode, identified by a non-None `DemoContext`. The `DemoHeader` widget (a `Label` subclass) currently renders static text set once at construction. `SlideScreen` already runs an async worker during the slide display window to call the LLM backend for the "what's new" explanation. `BotConfig` in Pydantic schema drives all per-bot metadata.

## Goals / Non-Goals

**Goals:**
- Insert preset prompts into the chat input with `Ctrl+Space` (one at a time, in order)
- Show remaining prompt count in `DemoHeader`; indicate exhaustion without crashing
- Translate prompts to `config.language` eagerly during the slide screen
- Keep the feature entirely behind the `demo_context is not None` guard

**Non-Goals:**
- Auto-send on `Ctrl+Space` — presenter always reviews before hitting Enter
- Wrapping or cycling when prompts are exhausted
- Prompt support outside demo mode
- Per-prompt language overrides

## Decisions

### D1: Prompts live on `DemoContext`, not looked up from config inside `ChatApp`

**Decision**: Add `prompts: list[str]` to `DemoContext`; populate it in `tui.py` from `config.bots[bot_type].prompts`.

**Rationale**: `DemoContext` is already the clean boundary for all demo-specific state. Keeping the config lookup in `tui.py` (where the bot type is known) avoids a `config` import inside `ChatApp` and gives translation a natural place to mutate the list.

**Alternative considered**: Have `ChatApp` call `config.bots.get(type(bot).__name__)` directly. Rejected because it couples the app to config lookup and makes translation harder to thread in.

### D2: Translation happens in `SlideScreen`, mutating `DemoContext.prompts` in place

**Decision**: `SlideScreen.on_mount()` launches a second async worker (alongside the existing explanation worker) that translates the prompts via the backend and replaces `self._demo_ctx.prompts`.

**Rationale**: The slide display window is a natural buffer — the presenter reads the slide while translation runs. Since `DemoContext` is a non-frozen dataclass, field reassignment is safe. If the presenter dismisses the slide before translation completes, `ChatApp` falls back to the original-language prompts.

**Alternative considered**: Translate lazily on first `Ctrl+Space`. Rejected because the delay would be visible mid-demo.

### D3: `DemoHeader` stores its data and overrides `render()` instead of using Textual `reactive`

**Decision**: Store `bot`, `position`, `_total_prompts`, and `_remaining` as instance fields; override `render()` to build the text dynamically; add `update_prompt_state(remaining: int)` that sets `_remaining` and calls `self.refresh()`.

**Rationale**: `Label.update()` and `self.refresh()` are sufficient for this use case. Full Textual `reactive` adds indirection for a single integer. The existing test pattern (`str(header.render())`) continues to work without modification.

**Alternative considered**: Textual `reactive` attribute with a `watch_` method. Rejected as over-engineered for one field.

### D4: `Ctrl+Space` key name

**Decision**: Use `"ctrl+space"` as the Textual key string, matching the Textual key-naming convention.

**Risk**: Some terminals send NUL (0x00) for Ctrl+Space, which may not arrive as `"ctrl+space"`. This must be verified on the target demo terminal before shipping. Fallback: `"ctrl+e"` if `"ctrl+space"` is unreliable.

### D5: Translation uses a single LLM call with a numbered-list format

**Decision**: Send all prompts in one call as a numbered list; parse the response by splitting on newline-and-digit patterns. No JSON output format.

**Rationale**: Minimal tokens, minimal parsing complexity. If the LLM returns a different count of items (rare), fall back to the original prompts silently.

## Risks / Trade-offs

- **Ctrl+Space terminal compatibility** → Test on the actual demo machine before the event; document `ctrl+e` as the fallback key if needed
- **Translation finishes after slide dismissed** → `ChatApp` uses original-language prompts as fallback; no crash, just English prompts
- **Translation count mismatch** → Fallback to original prompts if parsed count doesn't match
- **`DemoHeader.render()` override vs. `Label` internals** → `Label` is a stable Textual widget; `render()` override is the documented extension point
