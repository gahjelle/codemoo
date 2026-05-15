## Why

Bots (the LLM/context layer) currently return both a `ChatMessage` and a `list[ContextItem]` from `on_message`, but the message text is always identical to the last item's `AssistantMessageContent`. This is a layer violation: bots are constructing display objects they have no business owning. Removing the redundant return value makes the boundary explicit and simplifies every bot's `on_message` implementation.

## What Changes

- **BREAKING**: `ChatParticipant.on_message` return type changes from `tuple[ChatMessage | None, list[ContextItem]]` to `list[ContextItem]`
- `HumanParticipant.on_message` returns `[]` (no tuple)
- All bots drop `ChatMessage` construction from `on_message`; the app derives the display message from the last returned `ContextItem`
- `_collect_replies` in `ChatApp` derives the `ChatMessage` from the last item when it is an `AssistantMessageContent`; `thinking_time` decoration and `status.clear()` guard are updated accordingly
- Bots that use list comprehension + `.append()` to build `new_items` switch to a single list construction expression
- `RetryBot._escalation_message` is adjusted to return a `str` instead of a `ChatMessage` (the `ChatMessage` wrapper served only to carry text back through the tuple)

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `chat-participant`: The `ChatParticipant` protocol's `on_message` return type changes from `tuple[ChatMessage | None, list[ContextItem]]` to `list[ContextItem]`.

## Impact

- `src/codemoo/core/participant.py` — protocol and `HumanParticipant`
- All bot files in `src/codemoo/core/bots/`
- `src/codemoo/chat/app.py` — `_collect_replies`
- ~12 test files that unpack the current tuple return

## Non-goals

- No changes to `ContextItem`, `build_context`, or anything in `context_items.py` / `context_builder.py`
- The `message: ChatMessage` input parameter to `on_message` is unchanged
- `ErrorBot.format_error()` is unchanged — it returns a `ChatMessage` directly and is called by the error-handling path in `_collect_replies`, not by `on_message`
- No changes to the three-layer architecture
