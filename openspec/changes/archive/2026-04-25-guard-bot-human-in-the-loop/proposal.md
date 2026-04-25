## Why

The agentic loop (AgentBot) executes tool calls unconditionally — including destructive ones like shell commands and file writes. For the demo progression, GuardBot introduces the concept of human-in-the-loop: the agent pauses before dangerous actions and asks permission, making explicit that trust and control are separate design choices from capability.

## What Changes

- **New bot**: `GuardBot` (Cato 🔒) — standalone `ChatParticipant` that reimplements the AgentBot tool loop with an approval gate before any tool marked `requires_approval=True`
- **New field on `ToolDef`**: `requires_approval: bool = False` — declarative per-tool flag; `write_file` and `run_shell` set to `True`
- **New UI component**: `ApprovalModal` — a Textual `ModalScreen` that shows the proposed tool call and offers Approve / Deny / Deny with reason
- **New formatting utility**: `format_tool_call()` in `core/tools/formatting.py` — replaces the clumsy `_format_args` + `short_sig` logic in `CommentatorBot`, with proper per-value truncation using `…`
- **`CommentatorBot` cleanup**: adopt `format_tool_call()`, drop private `_format_args` and inline slicing
- **`ChatApp` wiring**: duck-typed detection of `register_guard` on any participant; wires the async approval callback

## Capabilities

### New Capabilities

- `guard-bot`: GuardBot (Cato) — the bot itself, its loop, `GuardDecision` type, `ApprovalRequest`, and `register_guard` registration pattern
- `approval-modal`: The `ApprovalModal` Textual widget and its three interaction states
- `tool-approval-flag`: The `requires_approval` field on `ToolDef` and which tools carry it

### Modified Capabilities

- `structured-tool-def`: Adding `requires_approval: bool = False` field to `ToolDef`
- `commentary-events`: `CommentatorBot` adopts `format_tool_call()`, dropping `_format_args` and `short_sig`
- `chat-ui`: `ChatApp` gains duck-typed guard registration and `_make_guard_ask_fn()`

## Non-goals

- Editing tool arguments before approval (rejected: multi-parameter tools make this impractical; the "deny with reason" path covers the use case more cleanly)
- Persisting approval decisions across sessions
- Per-tool granularity beyond the binary `requires_approval` flag
- Cancelling an in-progress worker from the UI (Ctrl-N already tears down cleanly via Textual's worker cancellation)

## Impact

- `src/codemoo/core/tools/__init__.py` — `ToolDef` gains new field; `format_tool_call` exported
- `src/codemoo/core/tools/formatting.py` — new module
- `src/codemoo/core/bots/guard_bot.py` — new module
- `src/codemoo/chat/approval.py` — new module
- `src/codemoo/core/bots/commentator_bot.py` — refactored to use `format_tool_call`
- `src/codemoo/chat/app.py` — guard registration wiring
- `configs/codemoo.toml` — GuardBot added to registry and default script
