## Why

When `complete()` is called without tools, LLM backends can still return a `ToolUse`
because the conversation history carries tool-call context from a prior turn. The
`or _INTERRUPTED` guard in `SingleTurnToolBot` only catches falsy values — a `ToolUse`
object is truthy and slips through, ultimately crashing with a `TypeError` when the
result is used as a string.

## What Changes

- `OpenAILikeBackend.complete()` guards the `tool_calls` branch with `if tools and message.tool_calls:`
- `_AnthropicBackend.complete()` guards the `tool_use` block branch with `if block.type == "tool_use" and tools:`
- When no tools were requested and the LLM returns a tool call anyway, both backends fall through to their text-extraction path and return `""` (empty string)
- The existing `or _INTERRUPTED` fallback in `SingleTurnToolBot` then surfaces `"(tool executed, process interrupted)"` as before — no change needed at the call site

## Capabilities

### New Capabilities

<!-- None -->

### Modified Capabilities

- `llm-completion`: backends must return `str` (never `ToolUse`) when `tools` is absent — the existing overload contract becomes a runtime guarantee

## Impact

- `src/codemoo/llm/openai_like.py` — one-line guard change
- `src/codemoo/llm/anthropic.py` — one-line guard change
- No API or interface changes; `SingleTurnToolBot` and all call sites are untouched

## Non-goals

- Retrying or looping on the second tool call — `SingleTurnToolBot` is intentionally single-turn
- Changing the `_INTERRUPTED` message text or surfacing it differently in the UI
- Fixing the underlying LLM behaviour (models returning tool calls without tool definitions)
