## Context

`ApprovalModal` is a Textual `ModalScreen` with three interaction paths: Approve, Deny, and Deny with reason. The "Deny with reason" path shows an `Input` widget and dismisses via `on_input_submitted`. In Textual, `Input.Submitted` is a bubbling message — it propagates from the widget, up through the modal screen, to the `App`. `ChatApp` also defines `on_input_submitted`, which dispatches a new agentic worker from any submitted input text. As a result, the denial reason text is mistakenly treated as a user chat message, spawning a concurrent worker that pushes its own approval modals.

The plain "Deny" path uses a button click (`Button.Pressed`), which does not reach `ChatApp.on_input_submitted`, so it is unaffected.

## Goals / Non-Goals

**Goals:**
- Stop `Input.Submitted` from propagating out of `ApprovalModal` after the modal dismisses
- Strengthen denial messages so the LLM is less likely to retry denied tool calls

**Non-Goals:**
- Changing the timing / future-resolution pattern in `_make_guard_ask_fn` (not the cause of the observed bug)
- Preventing the LLM from ever retrying a denied operation
- Any UX changes to the approval flow

## Decisions

### Call `event.stop()` in `ApprovalModal.on_input_submitted`

After `self.dismiss(...)`, add `event.stop()` to halt propagation. This is the idiomatic Textual fix — handlers call `event.stop()` when they fully own the event and don't want parent widgets or screens to react to it.

**Alternative considered**: Override `on_input_submitted` on `ChatApp` to ignore events originating from modal screens. Rejected — fragile, requires inspecting event source, doesn't fix the root cause.

### Strengthen denial message for no-reason denials

Change `"The user denied this tool call."` to `"The user denied this tool call. Do not attempt it again — move on to the next step."`. The reason-based message (`f"Tool call denied: {reason}"`) already carries the user's instruction and is left unchanged.

**Alternative considered**: Return a tool error instead of a tool result on denial. Rejected — some LLM backends treat tool errors differently and may stop the loop; a strong instruction in the result is safer.

## Risks / Trade-offs

- `event.stop()` after `dismiss` is safe: the modal is already being removed from the screen. No other handler should need this event.
- Stronger denial text is a heuristic — it reduces retries but cannot guarantee the LLM won't retry. Accepted as sufficient per the proposal.
