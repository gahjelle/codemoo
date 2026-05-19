## 1. Rename capability string

- [x] 1.1 In `src/codemoo/config/schema.py`, change `BotCapability = Literal["context_management"]` to `Literal["context_display"]`
- [x] 1.2 In `src/codemoo/chat/app.py`, rename the `"context_management"` key in `_CAPABILITY_BINDERS` to `"context_display"`
- [x] 1.3 In `src/codemoo/config/codemoo.toml`, replace all 8 occurrences of `capabilities = ["context_management"]` with `capabilities = ["context_display"]`

## 2. Lift Ctrl-R out of demo mode

- [x] 2.1 In `ChatApp.on_key`, move the `ctrl+r` branch before the `if self._demo_context is None: return` guard and add an explicit `return` after calling `_restart_bot()`
- [x] 2.2 In `ChatApp._restart_bot`, remove the `if self._demo_context is None: return` guard at the top
- [x] 2.3 In `ChatApp._restart_bot`, wrap the `prompts = self._demo_context.prompts` and `self.query_one(DemoHeader).update_prompt_state(len(prompts))` lines in `if self._demo_context is not None:`

## 3. Implement ContextInspectModal

- [x] 3.1 Create `src/codemoo/chat/context_inspect.py` with `ContextInspectModal(ModalScreen)` that accepts `items: list[ContextItem]` and `token_count: int`
- [x] 3.2 Implement `_format_row(item: ContextItem) -> str` as a module-level pure function: mode glyph + optional `📌` + 4-char type tag + preview; use `_format_tokens` from `context_status.py` for the header
- [x] 3.3 Implement preview formatting for each `ContextContent` type: plain text for `UserMessageContent`, `AssistantMessageContent`, `SystemContent`; `[{label}] {text}` for `InjectedContent`; `{name}({first_key}="{val}") → {output[:25]}` for `ToolUseContent` (fall back to `{name}(...)` on parse error)
- [x] 3.4 Implement `compose()`: header `Label`, then a `VerticalScroll` body that interleaves item `Label`s with dim turn-separator `Label`s between adjacent items whose `turn_id` differs
- [x] 3.5 Add CSS for the modal to `src/codemoo/chat/chat.tcss`: `width: 90%`, centred, appropriate background and border consistent with other modals; dim style for separator labels

## 4. Wire Ctrl-X into ChatApp

- [x] 4.1 Import `ContextInspectModal` in `src/codemoo/chat/app.py`
- [x] 4.2 Add a `_last_token_count: int = 0` instance attribute to `ChatApp.__init__` and update it in `_dispatch` alongside the `ContextStatus` update
- [x] 4.3 In `ChatApp.on_key`, add a `ctrl+x` branch (before the demo-mode guard) that checks `"context_display" in self._active_capabilities` and pushes `ContextInspectModal(self._chat_context, self._last_token_count)`

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 5.2 Run `uv run ty check src/ tests/`
- [x] 5.3 Run `uv run pytest` and confirm all tests pass
- [x] 5.4 Launch `uv run codemoo` (non-demo), send a message, press Ctrl-X to confirm the modal opens with context items; press Escape to close; press Ctrl-R to confirm restart works without crashing
- [x] 5.5 Launch `uv run codemoo demo`, confirm Ctrl-R still resets prompt index and updates DemoHeader; confirm Ctrl-X opens the inspector

## 6. Documentation

- [x] 6.1 Read `AGENTS.md` and update the `context_management` capability reference in the "Bot Configuration" section to `context_display`; update the shortcut table in "Demo Mode Keyboard Shortcuts" if Ctrl-R wording needs adjusting
- [x] 6.2 Read `PLANS.md` and delete the "Include Ctrl-R (restart) outside of demo mode" task and the "Add context management capability that can customize context" task (the display part is now done; the editing part remains future work — add a note if appropriate)
