## 1. Bot List Filtering and DemoContext

- [x] 1.1 Update `_setup()` in `tui.py` to return the backend alongside the existing tuple
- [x] 1.2 Define `DemoContext` dataclass in `slides.py` with fields: `all_bots`, `prev_bot`, `backend`, `position`
- [x] 1.3 Update `demo()` in `tui.py` to slice `available[index:]` into `demo_bots` and build `DemoContext` per iteration
- [x] 1.4 Update `ChatApp.__init__` to accept `demo_context: DemoContext | None` replacing `demo_position`
- [x] 1.5 Update `DemoHeader` construction in `ChatApp.compose()` to use `demo_context.position`
- [x] 1.6 Update `on_key` Ctrl-N handler in `ChatApp` to check `demo_context` instead of `demo_position`

## 2. Static Demo Data

- [x] 2.1 Create `slides_data.py` with `BOT_DESCRIPTIONS: dict[type, str]` — one-liner per bot type for EchoBot through AgentBot
- [x] 2.2 Add `BOT_SOURCES: dict[type, list[str]]` to `slides_data.py` — source file list per bot type, with `general_tool_bot.py` included for ToolBot, FileBot, ShellBot

## 3. Agenda Column Widget

- [x] 3.1 Implement `AgendaColumn` widget in `slides.py` — accepts `all_bots` and `current_index`
- [x] 3.2 Render each bot as `{emoji} {name}` with CSS classes: `agenda--past` (dimmed), `agenda--current` (highlighted), `agenda--upcoming` (normal)
- [x] 3.3 Add `AgendaColumn` CSS to `chat.tcss` (structural: fixed width; visual: colors/opacity)

## 4. Slide Content Widget

- [x] 4.1 Implement `SlideContent` widget in `slides.py` — accepts current bot, `prev_bot | None`, and `backend`
- [x] 4.2 Render title (`"Meet {name}, a {BotType}"`), one-liner from `BOT_DESCRIPTIONS`, and a scrollable "what's new" area
- [x] 4.3 Show `"Generating…"` placeholder in the "what's new" area on mount
- [x] 4.4 Implement `_build_llm_prompt()` — reads source files from `BOT_SOURCES`, includes tool names if bot has `.tools`, branches on first-bot vs comparison
- [x] 4.5 Fire async worker in `on_mount` to call `backend.complete()` with the prompt and replace the placeholder when done
- [x] 4.6 Add `SlideContent` CSS to `chat.tcss`

## 5. Slide Screen

- [x] 5.1 Implement `SlideScreen(ModalScreen)` in `slides.py` — compose with `Horizontal(AgendaColumn, SlideContent)` and an OK `Button`
- [x] 5.2 Wire OK button `on_button_pressed` to `self.dismiss()`
- [x] 5.3 Wire `on_key` to dismiss on Enter and Escape
- [x] 5.4 Add `SlideScreen` modal CSS to `chat.tcss`
- [x] 5.5 Push `SlideScreen` in `ChatApp.on_mount()` when `demo_context` is set

## 6. Tests

- [x] 6.1 Unit tests for `AgendaColumn`: correct CSS classes for past/current/upcoming positions
- [x] 6.2 Unit tests for `_build_llm_prompt()`: first-bot path, comparison path, tools-list inclusion
- [x] 6.3 Unit tests for `SlideScreen`: OK/Enter/Escape all trigger dismiss
- [x] 6.4 Update existing `test_chat_app_demo.py` for the new `DemoContext` constructor signature
- [x] 6.5 Update `test_demo_header.py` if `DemoHeader` construction changes
