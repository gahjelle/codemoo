## Why

During a live demo it's useful to reopen the current bot's slide mid-chat — to revisit a code explanation or re-anchor the audience after a detour. There is currently no way to do this without restarting the session.

## What Changes

- Add a **Ctrl-S** key binding in demo-mode `ChatApp` that reopens the current bot's `SlideScreen` as a modal overlay
- Cache the LLM-generated slide explanation in `DemoContext` so that reopening the slide is instant and shows the same text
- Chat history is unaffected: `SlideScreen` is already a `ModalScreen`; the underlying `ChatApp` (and its `_history`) is untouched while the modal is visible

## Non-goals

- Changing the slide content or regenerating the LLM explanation when reopened
- Adding a visual indicator in the chat that the slide was reopened
- Supporting slide navigation (previous/next bot slides) from within a session

## Capabilities

### New Capabilities

_(none — this extends two existing capabilities)_

### Modified Capabilities

- `demo-mode`: add Ctrl-S requirement — pressing Ctrl-S in demo mode SHALL reopen the current bot's slide as a modal overlay
- `demo-slide-screen`: add LLM text caching requirement — the generated explanation SHALL be cached in `DemoContext` so that reopening produces the same text instantly

## Impact

- `src/codemoo/chat/slides.py` — `DemoContext` gets a new `cached_explanation` field; `SlideContent._load_explanation()` reads and writes the cache
- `src/codemoo/chat/app.py` — `ChatApp.on_key` gains a `ctrl+s` branch that calls `push_screen(SlideScreen(self._demo_context))`
- No new dependencies; no API changes; no breaking changes
