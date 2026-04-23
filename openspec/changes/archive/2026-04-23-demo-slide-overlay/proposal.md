## Why

The demo mode progresses through bots mechanically — the audience has no moment to orient before each chat session begins. A slide screen between sessions gives the presenter a structured pause to introduce each bot, explain what's new, and set expectations.

## What Changes

- **New slide screen**: A `ModalScreen` is pushed before each bot's chat session in demo mode, showing a two-column layout: an Agenda column listing all bots in the session, and a content area with the bot's introduction and an LLM-generated "what's new" explanation.
- **Bot session filtering**: `demo()` slices `available[index:]` to produce `demo_bots` — the bots in this session. Position numbering, the Agenda, and all comparisons use this filtered list. `--start rune` produces `[Rune, Ash, Loom]`; earlier bots don't exist.
- **DemoContext dataclass**: Bundles `all_bots`, `prev_bot`, and `backend` — passed from `demo()` to `ChatApp` to `SlideScreen`.
- **Bot one-liners**: A new `slides_data.py` file holds one hard-coded description sentence per bot type, separate from the core bot classes.
- **Source file mapping**: `slides_data.py` also maps each bot type to its relevant source files for LLM context. `ToolBot`, `FileBot`, and `ShellBot` include `general_tool_bot.py` in addition to their own thin file.
- **Keyboard shortcuts**: Enter and Escape dismiss the slide in addition to the OK button.
- `_setup()` updated to return the backend alongside the existing return values.

## Capabilities

### New Capabilities

- `demo-slide-screen`: Full overlay screen shown before each bot session in demo mode. Includes an Agenda column (emoji + name, dimmed/highlighted/normal) and a content area (title, one-liner, async LLM "what's new" explanation, OK button).
- `demo-bot-descriptions`: Static per-bot metadata: one-liner descriptions and source file mappings, stored in `slides_data.py`.

### Modified Capabilities

- `demo-mode`: The demo loop now passes a filtered bot list and DemoContext. Position numbering reflects the session's bot list, not the full available list. The slide screen is shown before each bot session.

## Impact

- **New files**: `src/codemoo/chat/slides.py`, `src/codemoo/chat/slides_data.py`
- **Modified files**: `src/codemoo/frontends/tui.py`, `src/codemoo/chat/app.py`, `src/codemoo/chat/chat.tcss`
- **No changes** to core bot classes, `make_bots()`, or any LLM backend
- **New Textual dependency usage**: `ModalScreen`, `Horizontal`, `VerticalScroll` (already available via textual)
