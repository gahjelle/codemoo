## 1. BotRestartEvent and commentator handler

- [x] 1.1 Add `BotRestartEvent` frozen dataclass to `src/codemoo/core/bots/commentator_bot.py` with field `bot_name: str`
- [x] 1.2 Add `_comment_on_restart(event: BotRestartEvent)` method to `CommentatorBot` — dim prefix `↺ Restarted`, LLM prompt asking for in-character reaction to fresh start, Streik fallback mentioning bot name
- [x] 1.3 Add `BotRestartEvent` to the `comment()` union type and dispatch it to `_comment_on_restart`

## 2. Divider widget and CSS

- [x] 2.1 Add a `restart-divider` CSS class rule to `src/codemoo/chat/chat.tcss` (e.g. full-width, dim color, centered text)
- [x] 2.2 In `ChatApp._restart_bot()`, synchronously mount a `Label("↺ Restarted", classes="restart-divider")` into the `#log` VerticalScroll

## 3. ChatApp restart logic

- [x] 3.1 Add `_restart_bot()` method to `ChatApp` in `src/codemoo/chat/app.py`:
  - mount the divider label in `#log`
  - call `await self._commentator_bot.comment(BotRestartEvent(...))` if commentator is set (use `run_worker` for the async call)
  - reset `self._history = []`
  - reset `self._prompt_index = 0`
  - update `DemoHeader` remaining count to full total via `update_prompt_state`
  - call `self.run_worker(self._run_startup())`
- [x] 3.2 Add `elif event.key == "ctrl+r": self._restart_bot()` to `on_key` in `ChatApp`

## 4. DemoHeader hint line

- [x] 4.1 Add `"Ctrl-R: restart"` to the `parts` list in `DemoHeader._build_text()` in `src/codemoo/chat/demo_header.py`

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/` and fix any formatting issues
- [x] 5.2 Run `uv run ruff check src/ tests/` and fix any lint errors
- [x] 5.3 Run `uv run ty check src/ tests/` and fix any type errors
- [x] 5.4 Run `uv run pytest` and confirm all tests pass
- [ ] 5.5 Manual smoke-test: launch demo mode, send a message, press Ctrl-R, verify divider appears, commentator quips, history is cleared, Ctrl-E restarts from first prompt

## 6. Documentation

- [x] 6.1 Read `AGENTS.md` and update if any demo-mode keyboard shortcut documentation needs adding
