## Context

After the `context-item-model` change, `on_message` returns `tuple[ChatMessage | None, list[ContextItem]]`. The `ChatMessage` component is display-only: its `text` is always identical to the last `ContextItem`'s `AssistantMessageContent.text`. Bots construct it solely to satisfy the return type, not because they need to produce a display object.

`on_message` is the centerpiece of the demo. Every bot in the progression reimplements it, and the slide diffs between consecutive bots must be minimal and deliberate. Any incidental complexity in the signature leaks into every bot and makes those diffs noisier than they need to be.

## Goals / Non-Goals

**Goals:**
- Remove the `ChatMessage` from the `on_message` return contract
- Keep all bot `on_message` bodies as clean and consistent as possible — implementation details must not vary between bots unless the variation makes a pedagogical point
- Apply consistent style rules across all bots as part of this pass:
  - Explicit type hints only when the type cannot be inferred (e.g. `tool_use_items: list[ToolUseContent] = []`)
  - List construction over list mutation (no `.append()` after a comprehension)

**Non-Goals:**
- Changes to `ContextItem`, `build_context`, or the three-layer architecture
- Changes to the `message: ChatMessage` input parameter
- Changes to `ErrorBot.format_error()` — it returns a `ChatMessage` directly via a separate path

## Decisions

### Return `list[ContextItem]` directly

**Decision**: Change the return type to `list[ContextItem]`.

**Rationale**: The `ChatMessage` was always derivable from the last item. Returning it separately forced every bot to construct a display object it had no ownership over. The app is the right place to perform the derivation, since it owns the display layer.

**Alternative considered**: Keep the tuple but make `ChatMessage` optional and deprecate it. Rejected — it adds complexity without benefit and leaves the layer violation in place.

### App derives `ChatMessage` from last `ContextItem`

**Decision**: In `_collect_replies`, after `await participant.on_message(...)`, check `if new_items and isinstance(new_items[-1].content, AssistantMessageContent)` and construct `ChatMessage(sender=participant.name, text=new_items[-1].content.text)`.

**Rationale**: The derivation rule is simple and universal across all bots. Centralising it in the app means bots never need to think about it.

**`thinking_time` decoration**: Attach `thinking_time` to the derived `ChatMessage` after construction, just as it was attached before. No semantic change — the decoration was always a display-layer concern.

**`status.clear()` guard**: The `finally` block currently guards on `reply is None`. After the change there is no `reply` variable from `on_message`. The guard should instead check whether the derivation produced a message (i.e. whether `new_items` yielded a reply). Concretely: derive the reply inside the try block; the finally guard checks `reply is None` on the locally derived variable.

### `RetryBot._escalation_message` returns `str`

**Decision**: Change `_escalation_message` to return `str` instead of `ChatMessage`.

**Rationale**: The helper was only called to extract `.text` from the returned `ChatMessage`. With no `ChatMessage` in the return contract, the wrapper is dead weight. Returning a plain string is simpler and consistent with how `response` is used throughout the other bots.

### List construction over mutation

**Decision**: Replace list comprehension + `.append()` patterns with a single list expression: `[*[ContextItem(...) for tu in tool_use_items], ContextItem(content=AssistantMessageContent(response), ...)]`.

**Rationale**: Mutation after construction is harder to read and inconsistent with how simpler bots build their item list. A single expression is clearer and matches the functional style of the rest of the codebase.

## Risks / Trade-offs

- **Stale tests**: ~12 test files unpack `(reply, new_items)`. All must change. Low risk — the compiler and tests will surface every missed site immediately.
- **`finally` guard correctness**: The `reply is None` check in `_collect_replies` must be preserved in semantics (status cleared when no reply is produced). Requires care during the app update but is a single, self-contained change.
