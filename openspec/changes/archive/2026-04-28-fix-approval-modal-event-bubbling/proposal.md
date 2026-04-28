## Why

When the user denies a GuardBot tool call using "Deny with reason", the `Input.Submitted` event bubbles from the modal up to `ChatApp`, which treats the denial reason text as a new user message and dispatches a second concurrent agentic worker. This causes stacked approval modals and spurious conversations. Additionally, denial messages are weak enough that the LLM sometimes retries the denied operation.

## What Changes

- `ApprovalModal.on_input_submitted` stops event propagation after dismissing, so the denial reason cannot reach `ChatApp.on_input_submitted`
- `_denial_message` in `GuardBot` is strengthened to discourage the LLM from retrying denied tool calls

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `approval-modal`: The reason-input submission path must stop event propagation after dismissing, preventing the denial reason from being dispatched as a chat message.
- `guard-bot`: Denial message text is updated to more firmly instruct the LLM not to retry the denied operation.

## Impact

- `src/codemoo/chat/approval.py` — add `event.stop()` in `on_input_submitted`
- `src/codemoo/core/bots/guard_bot.py` — update `_denial_message` return values

## Non-goals

- Fixing any timing / race condition in the `_make_guard_ask_fn` future-based pattern (this appears not to be the cause of the observed bug)
- Changing the approval flow UX or adding new interaction paths
- Preventing the LLM from ever retrying denied operations (strengthening the message is sufficient)
