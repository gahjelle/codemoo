## 1. Cache LLM explanation in DemoContext

- [x] 1.1 Add `cached_explanation: str | None = None` field to `DemoContext` dataclass in `src/codemoo/chat/slides.py`
- [x] 1.2 Update `SlideContent._load_explanation()` to return immediately (populating the `#slide-whats-new` Markdown widget) if `DemoContext.cached_explanation` is already set
- [x] 1.3 After a successful LLM call in `_load_explanation()`, write the result to `DemoContext.cached_explanation` before updating the widget

## 2. Add Ctrl-S key binding to ChatApp

- [x] 2.1 In `ChatApp.on_key` (`src/codemoo/chat/app.py`), add an `elif event.key == "ctrl+s":` branch that calls `self._reopen_slide()`
- [x] 2.2 Implement `ChatApp._reopen_slide()`: guard against stacking (check if a `SlideScreen` is already on the screen stack), then call `self.push_screen(SlideScreen(self._demo_context))`
- [x] 2.3 Ensure the guard and key binding are no-ops when `self._demo_context is None`

## 3. Verification

- [x] 3.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 3.2 Run `uv run ty check src/ tests/`
- [x] 3.3 Run `uv run pytest` and confirm all tests pass
- [x] 3.4 Manual smoke test: launch `uv run codemoo demo`, dismiss the initial slide, send a message, press Ctrl-S, confirm the slide reopens with cached text, dismiss, confirm chat history intact
- [x] 3.5 Manual edge case: press Ctrl-S while the slide is already open — confirm no second modal is pushed

## 4. Documentation

- [x] 4.1 Read `README.md`, `AGENTS.md`, and any relevant docs; update keyboard shortcut references (e.g. where Ctrl-N and Ctrl-E are documented) to mention Ctrl-S
