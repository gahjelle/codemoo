## 1. Tool formatting utility

- [x] 1.1 Create `src/codemoo/core/tools/formatting.py` with `format_tool_call(name, arguments, *, max_value_len=None)` — per-value truncation with `…`, newline→space normalisation
- [x] 1.2 Export `format_tool_call` from `src/codemoo/core/tools/__init__.py`
- [x] 1.3 Write tests for `format_tool_call` covering: no truncation, truncation at boundary, empty args, non-string values, newlines in values

## 2. ToolDef requires_approval field

- [x] 2.1 Add `requires_approval: bool = False` field to `ToolDef` dataclass in `src/codemoo/core/tools/__init__.py`
- [x] 2.2 Set `requires_approval=True` on `run_shell` and `write_file` tool definitions
- [x] 2.3 Update existing `ToolDef` tests to confirm `requires_approval` defaults to `False`

## 3. CommentatorBot refactor

- [x] 3.1 Replace `_format_args` calls in `CommentatorBot.comment()` with `format_tool_call(event.tool_name, event.arguments)` for the LLM prompt (no truncation)
- [x] 3.2 Replace the `call_sig` + `short_sig` inline slicing with `format_tool_call(..., max_value_len=40)` for the display header
- [x] 3.3 Delete the private `_format_args` function
- [x] 3.4 Verify existing `CommentatorBot` tests still pass; add a test asserting the display header uses `…` on long values

## 4. GuardDecision types and ApprovalRequest

- [x] 4.1 Create `src/codemoo/core/bots/guard_bot.py` with `Approved`, `Denied`, `GuardDecision`, and `ApprovalRequest` dataclasses
- [x] 4.2 Write unit tests for `GuardDecision` construction and field access

## 5. GuardBot implementation

- [x] 5.1 Implement `GuardBot` dataclass in `guard_bot.py`: fields `name`, `emoji`, `backend`, `human_name`, `tools`, `instructions`, `max_messages`, `commentator`; `is_human = False`
- [x] 5.2 Implement `register_guard(ask_fn)` with default no-op that returns `Approved()`
- [x] 5.3 Implement `on_message` tool loop: mirror AgentBot's loop, add approval gate before any `tool.requires_approval` tool
- [x] 5.4 Implement denial message formatting: plain deny → `"The user denied this tool call."`, deny with reason → `f"Tool call denied: {reason}"`
- [x] 5.5 Write unit tests for GuardBot: safe tools bypass gate, dangerous tools invoke ask_fn, Approved runs tool, Denied returns denial string, Denied-with-reason includes reason
- [x] 5.6 Add `GuardBot` to `src/codemoo/core/bots/__init__.py` exports and `make_bots` factory

## 6. ApprovalModal widget

- [x] 6.1 Create `src/codemoo/chat/approval.py` with `ApprovalModal(ModalScreen[GuardDecision])`
- [x] 6.2 Implement initial state: display `"🔒 {bot_name} wants to call {tool_call}"` using `format_tool_call(..., max_value_len=80)`, plus Approve / Deny / Deny-with-reason buttons
- [x] 6.3 Implement reason-input state: hide buttons, show `"What should {bot_name} do instead?"` label and a focused `Input` widget
- [x] 6.4 Wire Approve button → `self.dismiss(Approved())`
- [x] 6.5 Wire Deny button → `self.dismiss(Denied(reason=None))`
- [x] 6.6 Wire Deny-with-reason button → transition to reason-input state
- [x] 6.7 Wire Input submission: non-empty → `Denied(reason=value)`, empty → `Denied(reason=None)`
- [x] 6.8 Add CSS to `chat.tcss` for the modal layout (centered container, button row, reason label)

## 7. ChatApp wiring

- [x] 7.1 Add `_make_guard_ask_fn()` method to `ChatApp`: creates `asyncio.Future[GuardDecision]`, calls `push_screen(ApprovalModal(request), future.set_result)`, returns `await future`
- [x] 7.2 In `ChatApp.__init__`, iterate participants and call `participant.register_guard(ask_fn)` for any participant with that attribute
- [x] 7.3 Import `ApprovalModal` and `GuardDecision` in `app.py`

## 8. Config and demo integration

- [x] 8.1 Add `[bots.GuardBot]` section to `configs/codemoo.toml` with `name = "Cato"`, `emoji = "LOCK"`, `description`, `sources = ["guard_bot.py"]`, and three demo `prompts`
- [x] 8.2 Add `"GuardBot"` to the `default` script list in `configs/codemoo.toml` (after `AgentBot`)
- [x] 8.3 Set `main_bot = "GuardBot"` in `configs/codemoo.toml`
- [x] 8.4 Verify `uv run codemoo demo` cycles correctly through AgentBot → GuardBot with the new slide

## 9. Final checks

- [x] 9.1 Run `uv run pytest` — all tests pass
- [x] 9.2 Run `uv run ruff check . && uv run ruff format .` — no lint/format issues
- [x] 9.3 Run `uv run ty check .` — no type errors
- [x] 9.4 Manual smoke test: run GuardBot, trigger `write_file`, verify modal appears; approve, deny, and deny-with-reason all behave correctly
