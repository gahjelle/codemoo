## 1. Commentary Event Protocol

- [x] 1.1 Create `ToolCallEvent` frozen dataclass in `commentator_bot.py` with fields `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`

## 2. CommentatorBot Core

- [x] 2.1 Define `Persona` dataclass (name, emoji, instructions) and the four personas: Arne (enthusiastic), Herwich (formal), Sølve (dry/terse), Rike (skeptical)
- [x] 2.2 Implement `CommentatorBot` dataclass with `backend: LLMBackend`, `_post_fn` (no-op default), and `register(post_fn)` method
- [x] 2.3 Implement `comment(event: ToolCallEvent) -> None`: pick random persona, build prompt, call LLM, post `ChatMessage`
- [x] 2.4 Implement Streik fallback in `comment()`: catch all exceptions, post hardcoded `"{bot_name} calls {tool_name}({formatted_args})"` from sender "Streik" with emoji 🪧

## 3. Bot Integration

- [x] 3.1 Add optional `commentator: CommentatorBot | None = None` field to `GeneralToolBot`
- [x] 3.2 Add `await self.commentator.comment(ToolCallEvent(...))` call in `GeneralToolBot.on_message` before tool invocation
- [x] 3.3 Add optional `commentator: CommentatorBot | None = None` field to `AgentBot`
- [x] 3.4 Add `await self.commentator.comment(ToolCallEvent(...))` call in `AgentBot.on_message` loop before tool invocation

## 4. Chat UI Wiring

- [x] 4.1 Add `bubble--commentator` CSS rule to `chat.tcss` with a soft grey background
- [x] 4.2 Add fallback path in `ChatApp._append_to_log`: use `("💬", False, "bubble--commentator")` when sender not in `_sender_info`
- [x] 4.3 Add `commentator_bot` parameter to `ChatApp.__init__`; call `commentator_bot.register(self._append_to_log)` there

## 5. Frontend Wiring

- [x] 5.1 Construct `CommentatorBot` in `tui.py` and pass it to `ChatApp` and to each tool-enabled bot

## 6. Tests

- [x] 6.1 Unit test `ToolCallEvent` field assignment
- [x] 6.2 Unit test `CommentatorBot.comment()` happy path: mock backend, assert post callback receives `ChatMessage` with a persona sender
- [x] 6.3 Unit test Streik fallback: mock backend to raise, assert post callback receives `ChatMessage` with sender "Streik" and correct text format
- [x] 6.4 Unit test `GeneralToolBot.on_message` with commentator: assert `comment()` is awaited before tool `fn`
- [x] 6.5 Unit test `AgentBot.on_message` with commentator: assert `comment()` is awaited on each tool call in a multi-step loop
- [x] 6.6 Unit test fallback sender-lookup in `ChatApp._append_to_log`: unknown sender gets `bubble--commentator` class
