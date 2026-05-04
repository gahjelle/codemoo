## Context

`SingleTurnToolBot` makes two sequential LLM calls: the first with tools enabled (to
let the LLM request a tool call), and the second without tools (to get a plain-text
reply after the tool result is injected). The second call relies on `or _INTERRUPTED`
to catch empty/falsy responses.

The bug: the `follow_up` message list carries the first assistant turn, which contains
`tool_calls`. Some models follow the conversational pattern they see and emit another
tool call even when no tools are defined in the request. Both backends return `ToolUse`
unconditionally when they detect tool calls in the response — regardless of whether
tools were in the request. `ToolUse` is truthy, so `or _INTERRUPTED` does not fire,
and a `ToolUse` lands in `ChatMessage.text`, causing a `TypeError` downstream.

## Goals / Non-Goals

**Goals:**
- Backends return `str` (never `ToolUse`) when `complete()` is called without tools
- Graceful `_INTERRUPTED` path restored in `SingleTurnToolBot` with no call-site changes

**Non-Goals:**
- Changing bot looping behaviour or retry logic
- Altering the public `LLMBackend` protocol or overload signatures
- Handling the symmetric case where tools are passed but the LLM returns plain text (already correct)

## Decisions

### Guard tool-call detection on whether tools were requested

Add `and tools` to the `ToolUse` return branch in each backend, so the path is only
taken when tools were actually part of the request:

```python
# openai_like.py  (was: if message.tool_calls:)
if tools and message.tool_calls:
    ...
    return ToolUse(...)

# anthropic.py  (was: if block.type == "tool_use":)
if block.type == "tool_use" and tools:
    ...
    return ToolUse(...)
```

When `tools` is `None` or `[]` and the LLM returns tool calls anyway, both backends
fall through to their text-extraction path and return `""`.

**Alternatives considered:**

- *Guard in `single_turn_tool_bot.py` with `isinstance(response, str)`*: Works, but
  adds type-checking noise to demo-visible code. Deferred type errors are worse than
  enforcing the contract at the source.
- *Raise an exception in the backend*: Too disruptive — the model behaving unexpectedly
  is not a programming error that should crash the process.
- *Return `_INTERRUPTED` directly from the backend*: Leaks call-site semantics into the
  backend layer.

## Risks / Trade-offs

- **Silently drops a tool call**: If a model returns `tool_calls` and we ignore them,
  the user sees `(tool executed, process interrupted)` with no indication a second tool
  call was attempted. This is the same behaviour as before the refactor — acceptable for
  a single-turn bot by design.
- **Anthropic rarely hits this path**: The Anthropic API won't return `tool_use` blocks
  when `tools=[]`, so the guard there is defensive. Still worth adding for consistency
  and correctness.
