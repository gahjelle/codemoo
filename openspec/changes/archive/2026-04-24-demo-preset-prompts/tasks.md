## 1. Config Schema

- [x] 1.1 Add `prompts: list[str] = []` to `BotConfig` in `src/codemoo/config/schema.py`
- [x] 1.2 Add example `prompts` arrays to each bot entry in `configs/codemoo.toml`
- [x] 1.3 Update `tests/config/test_schema.py`: verify prompts field is parsed and defaults to `[]`

## 2. DemoContext

- [x] 2.1 Add `prompts: list[str]` field (default `[]`) to `DemoContext` dataclass in `src/codemoo/chat/slides.py`
- [x] 2.2 In `tui.py._run_demo`, extract prompts from `config.bots[bot_type]` and pass to `DemoContext`
- [x] 2.3 Update `_make_demo_context()` in `tests/chat/test_chat_app_demo.py` to accept/pass prompts

## 3. DemoHeader Reactivity

- [x] 3.1 Refactor `DemoHeader.__init__` to accept `prompt_count: int` and store `bot`, `position`, `_total`, `_remaining` as instance fields
- [x] 3.2 Override `render()` in `DemoHeader` to build text dynamically from stored fields, covering the four display states (no prompts / N left / last / exhausted)
- [x] 3.3 Add `update_prompt_state(remaining: int)` method that sets `_remaining` and calls `self.refresh()`
- [x] 3.4 Update `ChatApp.compose()` to pass `len(demo_context.prompts)` to `DemoHeader`
- [x] 3.5 Update `tests/chat/test_demo_header.py`: add tests for Ctrl-Space hint presence/absence and `update_prompt_state` output

## 4. Ctrl+Space Key Binding

- [x] 4.1 Add `_prompt_index: int = 0` to `ChatApp.__init__`
- [x] 4.2 Add `_insert_next_prompt()` method to `ChatApp`: reads `demo_context.prompts[_prompt_index]`, sets `Input.value`, increments index, calls `header.update_prompt_state(remaining)`
- [x] 4.3 Handle `"ctrl+space"` in `ChatApp.on_key`: call `_insert_next_prompt()` only when `demo_context is not None`
- [x] 4.4 Update `tests/chat/test_chat_app_demo.py`: test Ctrl+Space inserts prompt, exhaustion does nothing, inactive outside demo mode

## 5. Eager Translation

- [x] 5.1 Add `_translate_prompts()` async method to `SlideScreen`: single LLM call with numbered-list format, parses response, falls back to originals on count mismatch
- [x] 5.2 In `SlideScreen.on_mount()`, launch translation worker when `config.language != "English"` and prompts are non-empty; worker mutates `self._demo_ctx.prompts` in place
- [x] 5.3 Add tests for translation logic: verifies translated list replaces original; verifies fallback on count mismatch; verifies no call when language is English or prompts empty

## 6. Verification

- [x] 6.1 Run `uv run pytest` — all tests pass
- [x] 6.2 Run `uv run ruff check .` and `uv run ruff format .` — no lint or formatting issues
- [x] 6.3 Run `uv run ty check .` — no type errors
- [x] 6.4 Manually launch `uv run codemoo demo` and verify: Ctrl-E inserts the first prompt, subsequent presses cycle through remaining prompts, header count decrements correctly, pressing after exhaustion does nothing
- [x] 6.5 Verified on target demo terminal: Ctrl-E works reliably (Ctrl+Space did not work — key binding updated to Ctrl-E)
