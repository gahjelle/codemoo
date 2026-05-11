## 1. Create ChatInput widget

- [x] 1.1 Create `src/codemoo/chat/input.py` with `ChatInput(TextArea)` subclass
- [x] 1.2 Define `ChatInput.Submitted` message with `value: str` field
- [x] 1.3 Implement `_on_key`: intercept `ctrl+enter`, prevent default, post `Submitted` with stripped text if non-empty, then clear
- [x] 1.4 Implement `on_text_area_changed`: count lines, set `self.styles.height = clamp(line_count, 1, 4)`
- [x] 1.5 Verify `load_text()` triggers `Changed` (and therefore auto-grow); if not, call height update explicitly

## 2. Update ChatApp

- [x] 2.1 Replace `Input` import with `ChatInput` in `app.py`
- [x] 2.2 Replace `yield Input(...)` with `yield ChatInput(...)` in `compose()`
- [x] 2.3 Rename `on_input_submitted` to `on_chat_input_submitted` and update event type annotation
- [x] 2.4 Replace all `query_one(Input)` calls with `query_one(ChatInput)`
- [x] 2.5 Update `_insert_next_prompt` to use `load_text()` instead of `.value =`
- [x] 2.6 Remove unused `Input` import from `textual.widgets`

## 3. Update CSS

- [x] 3.1 Add `ChatInput` style block in `chat.tcss` (border, padding to match old `Input` look)
- [x] 3.2 Remove or replace any `Input`-specific CSS rules that no longer apply

## 4. Verification

- [x] 4.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 4.2 Run `uv run ty check src/ tests/`
- [x] 4.3 Run `uv run pytest`
- [x] 4.4 Manually test: single-line prompt submits on Ctrl+Enter, Enter adds newline, auto-grow 1→4 rows
- [x] 4.5 Manually test: paste multiline text (Ctrl-V) renders correctly and expands widget
- [x] 4.6 Manually test: Ctrl-E demo prompt insertion fills widget and auto-grows

## 5. Documentation

- [x] 5.1 Review README.md, PLANS.md, BOTS.md, and AGENTS.md; update if any references to the input field or keyboard shortcuts need changing
