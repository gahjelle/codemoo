## 1. Verbatim bubble rendering

- [x] 1.1 In `_BubbleContent.compose` (`chat/bubble.py`), change the condition from `"bubble--commentator" in self.classes` to `"bubble--verbatim" in self.classes`
- [x] 1.2 Change the `Static` call to pass `markup=False` (currently `markup=True`)
- [x] 1.3 In `ChatApp.__init__` (`chat/app.py`), update `_sender_info` so commentator sender entries carry both `bubble--commentator` and `bubble--verbatim` CSS classes (the `commentator_bot.sender_info()` return value drives this — update `CommentatorBot.sender_info()` to return `"bubble--commentator bubble--verbatim"`)

## 2. Shell sender registration

- [x] 2.1 In `ChatApp.__init__`, add a fixed `"Shell"` entry to `_sender_info`: `("\N{COMPUTER}", "bubble--shell bubble--verbatim")`

## 3. Shell CSS class

- [x] 3.1 In `chat.tcss`, add a `bubble--shell` rule with a distinct background color (suggest a dark green tint, e.g. `$success` darkened, to signal terminal output)

## 4. `!`-prefix interception

- [x] 4.1 In `on_chat_input_submitted` (`chat/app.py`), before building the `ContextItem`, check `if text.startswith("!")` and branch into a separate `_handle_shell_input` async method (called via `run_worker`)
- [x] 4.2 Implement `_handle_shell_input(self, text: str) -> None`: strip the leading `!`, call `_run_shell(command)` (import from `codemoo.core.tools.shell`), then call `self._append_to_log` with a `ChatMessage` using sender `"Shell"` and the output, then call `self.copy_to_clipboard(output)`
- [x] 4.3 Ensure the human's `! command` input bubble is still appended to the log before dispatching the worker (mirrors existing bot-dispatch pattern)
- [x] 4.4 Confirm that `_chat_context` is NOT extended with the shell output (no `ContextItem` for the output)

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/`
- [x] 5.2 Run `uv run ruff check src/ tests/`
- [x] 5.3 Run `uv run ty check src/ tests/`
- [x] 5.4 Run `uv run pytest`
- [ ] 5.5 Manual smoke test: launch `uv run codemoo`, type `! ls`, verify shell bubble appears, verify clipboard contains the output, verify bots are not triggered
- [ ] 5.6 Manual edge case: type `! cat README.md`, verify Markdown syntax in the output renders as literal characters (no headers, no bold)

## 6. Documentation

- [x] 6.1 Read `AGENTS.md` and add a note about the `!`-prefix shell shortcut under the Demo Mode Keyboard Shortcuts section or a new "Shell Mode" section
