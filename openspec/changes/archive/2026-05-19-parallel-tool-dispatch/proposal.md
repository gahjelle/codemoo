## Why

When an LLM returns multiple tool calls in a single response, all backends silently discard calls 2..N, returning only the first as a single `ToolUse`. AgentBot and every bot built on the same pattern therefore loop one tool at a time — burning unnecessary LLM round-trips when the model already knew what it wanted to call next.

## What Changes

- **BREAKING** `complete()` return type changes from `str | ToolUse` to `str | list[ToolUse]` — callers that pattern-match on `isinstance(response, ToolUse)` must update to `isinstance(response, list)`
- Add pure helper `merge_tool_uses(uses: list[ToolUse]) -> Message` to `backend.py`; combines the individual `tool_calls_json` entries from each `ToolUse` into one combined assistant `Message` suitable for multi-call round-trips
- Anthropic backend: collect all `tool_use` blocks from response; fix `_serialize()` to merge consecutive `role="tool"` messages into a single batched user message (required by Anthropic's API for parallel tool results)
- OpenAI-like backend: collect all entries from `message.tool_calls`; no serialization change needed
- `SingleTurnToolBot`: adapts to `list[ToolUse]`, uses `response[0]` — behavior unchanged
- `AgentBot`: dispatches all requested tool calls per LLM response (sequential `for`-loop, since all tool functions are currently synchronous); uses `merge_tool_uses()` for the combined assistant message before the next `complete()` call
- `GuardBot`, `MemoryBot`, `ProjectBot`, `RetryBot`, `CompactBot`: same structural adaptation as `AgentBot`; `GuardBot` checks approval per-call in the loop

## Non-goals

- No true async parallelism (`asyncio.gather`) — all tool functions are synchronous; a `for`-loop is honest and sufficient
- No new bot type — `AgentBot` becomes the parallel version in place
- No changes to `ToolDef`, `dispatch_tool`, `ToolParam`, context items, commentator events, or approval UX

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `llm-completion`: **BREAKING** — return type changes from `str | ToolUse` to `str | list[ToolUse]`; adds `merge_tool_uses()` helper to the protocol module
- `agent-bot`: `AgentBot` now dispatches all tool calls returned in a single LLM response before the next `complete()` call, instead of one call per LLM round-trip

## Impact

- `src/codemoo/core/backend.py` — protocol signature and new helper
- `src/codemoo/llm/anthropic.py` — return all tool calls; fix serialization for batched tool results
- `src/codemoo/llm/openai_like.py` — return all tool calls
- `src/codemoo/core/bots/single_turn_tool_bot.py`
- `src/codemoo/core/bots/agent_bot.py`
- `src/codemoo/core/bots/guard_bot.py`
- `src/codemoo/core/bots/memory_bot.py`
- `src/codemoo/core/bots/project_bot.py`
- `src/codemoo/core/bots/retry_bot.py`
- `src/codemoo/core/bots/compact_bot.py`
- `src/codemoo/frontends/cli.py` — `tool()` uses `response[0]` like `SingleTurnToolBot`; `agent()` loops over all uses like `AgentBot`
- Tests for all modified bots and backends
