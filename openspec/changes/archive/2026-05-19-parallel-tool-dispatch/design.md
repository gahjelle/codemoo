## Context

The `LLMBackend.complete()` protocol currently returns `str | ToolUse`. Both the Anthropic and OpenAI-like backends receive a full list of tool calls from the API but silently discard all but the first, returning a single `ToolUse`. Every bot built on the agent loop (AgentBot and its five descendants) therefore processes one tool call per LLM round-trip, even when the model requested several.

The Anthropic API has an additional constraint: when an assistant message contains N tool calls, all N results must arrive in a single batched user message. The current serializer creates one user message per tool result, which works for sequential single-call flow but would break for parallel batches.

## Goals / Non-Goals

**Goals:**
- `complete()` returns all tool calls the LLM requested in one response
- AgentBot and all downstream bots dispatch every returned call before asking the LLM again
- Anthropic serialization correctly batches tool results when N > 1
- No observable behavior change for callers that only ever receive a single tool call

**Non-Goals:**
- Async/concurrent dispatch — all tool functions are synchronous; `asyncio.gather` gives no benefit today
- Introducing a new bot type for "parallel" behavior
- Changing `dispatch_tool`, `ToolDef`, context items, or commentary events

## Decisions

### Decision 1: `complete()` returns `list[ToolUse]`, not `str | ToolUse | list[ToolUse]`

**Chosen**: Return type becomes `str | list[ToolUse]`. A single tool call returns a one-element list. Callers check `isinstance(response, list)`.

**Alternative considered**: Extend `ToolUse` with `parallel_calls: list[ToolUse] = []`, keeping `str | ToolUse`. Existing bots see a `ToolUse` with the extra field silently ignored; only the new bot reads it.

**Why rejected**: Backward compatibility is illusory. An existing bot using `response.assistant_message` (which contains only one tool call) while ignoring the sibling calls would produce broken context on the next `complete()` call — the assistant message referenced N calls but only N−1 results were provided. The clean break forces callers to acknowledge all calls exist.

### Decision 2: Each `ToolUse.assistant_message` carries only its own call

**Chosen**: `ToolUse.assistant_message.tool_calls_json` contains a JSON array with exactly one entry — the same as today. Add `merge_tool_uses(uses: list[ToolUse]) -> Message` to `backend.py` to combine them when needed.

**Why**: `SingleTurnToolBot` picks `response[0]` and uses `response[0].assistant_message` directly. A single-call message is correct for that case — no orphaned tool-call IDs in context. `AgentBot` calls `merge_tool_uses()` to get the combined message when there are multiple calls. No coupling between individual `ToolUse` objects; each remains self-contained.

### Decision 3: Sequential `for`-loop in AgentBot (not `asyncio.gather`)

**Chosen**: Loop over all uses, `await dispatch_tool(...)` one at a time.

**Why**: Every tool function (`_read_file`, `_run_shell`, etc.) is synchronous. `asyncio.gather` on `dispatch_tool` coroutines would not provide actual concurrency — the sync calls block the event loop. A `for`-loop is honest and produces identical wall-clock performance. If tools become async in the future, the loop can be replaced with `gather` in one line.

### Decision 4: Anthropic `_serialize()` merges consecutive `role="tool"` messages

The `_serialize()` function in `anthropic.py` currently emits one `{"role": "user", "content": [tool_result]}` message per tool result. Anthropic's API rejects two consecutive user messages with tool results when they correspond to a single assistant tool-use batch.

**Fix**: In `_serialize()`, detect consecutive `role="tool"` messages and emit them as a single `{"role": "user", "content": [tool_result, tool_result, ...]}`. This is a no-op for the single-call case (one tool result still becomes one user message) and is required for multi-call batches.

No change to `openai_like.py` serialization — OpenAI accepts individual tool-result messages.

## Risks / Trade-offs

**[Risk] Existing tests mock `complete()` returning `ToolUse` directly** → All test fixtures and mocks that return a bare `ToolUse` must be updated to return `[ToolUse(...)]`. Risk of missed mocks causing runtime errors rather than test failures. Mitigation: `ty check` will catch any remaining `isinstance(response, ToolUse)` checks after the change.

**[Risk] Anthropic rejects batched tool results in some edge cases** → The merged-user-message path is exercised only when N > 1. Manual integration testing with a real multi-call prompt is needed to verify the Anthropic wire format is correct.

**[Risk] GuardBot approval flow with mixed safe/dangerous calls in a batch** → If the LLM requests [safe_tool, dangerous_tool] in one response, approval is requested per-call in the loop. The safe tool runs first; the user then approves or denies the dangerous one. This is reasonable but means tool execution order within a batch is not arbitrary — it follows the order the LLM returned them. Documented as intended behavior.

## Migration Plan

All changes are internal to the backend protocol and bot implementations. No external API, config format, or persistent storage changes. Rollback is a revert of the changed files. No staged deployment needed.

## Open Questions

_(none)_
