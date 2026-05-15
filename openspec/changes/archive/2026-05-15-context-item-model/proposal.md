## Why

The current architecture has no shapeable layer between chat history and the LLM wire format — each bot independently converts `list[ChatMessage]` into `list[Message]`, losing tool call traces between turns and providing no mechanism for context manipulation. Introducing an explicit `list[ContextItem]` layer makes context a first-class value that can be filtered, summarised, edited, extended with injected content, and role-reversed — both programmatically by bots and interactively by the user.

## What Changes

- **BREAKING** `ChatParticipant.on_message` signature changes from `(message, history: list[ChatMessage]) -> ChatMessage | None` to `(message, context: list[ContextItem]) -> tuple[ChatMessage | None, list[ContextItem]]`. All bots updated accordingly.
- New `ContextItem` immutable value type with: content (discriminated union), `turn_id`, `mode` (ORIGINAL / EDITED / SUMMARY / DISABLED), `edited`, `summary`, `role_override`, `pinned`.
- New `ContextContent` discriminated union: `UserMessageContent`, `AssistantMessageContent`, `ToolUseContent` (atomic call+result pair), `InjectedContent`, `SystemContent`.
- New pure `build_context(items: list[ContextItem]) -> list[Message]` function replacing per-bot inline context construction.
- `ChatApp` owns the authoritative `list[ContextItem]`, passing it into each `on_message` call and receiving the updated list back.
- `list[ContextItem]` is treated as immutable — all context operations are pure functions returning new lists.
- `turn_id` is assigned as `max(item.turn_id for item in context) + 1` when context is non-empty, else `0`.
- Bots that do not use context (EchoBot, LlmBot) follow the new protocol but ignore the incoming context, appending only their reply item.

## Capabilities

### New Capabilities

- `context-item`: The `ContextItem` type, `ContextContent` discriminated union, `ItemMode` enum, and pure operations on `list[ContextItem]` (add, replace, set_mode, set_edited, set_summary, inject_at).
- `context-builder`: The `build_context(items) -> list[Message]` pure function, including ToolUseContent unrolling and handling of DISABLED / EDITED / SUMMARY modes.

### Modified Capabilities

- `chat-participant`: `on_message` signature changes; `history: list[ChatMessage]` is replaced by `context: list[ContextItem]`; return type becomes `tuple[ChatMessage | None, list[ContextItem]]`.

## Non-Goals

- UI modal for interactive per-item context manipulation (separate change).
- LLM-powered automatic summary generation.
- Budget-aware context window trimming.
- Context persistence across sessions.
- Any changes to the LLM backend wire format or provider adapters.

## Impact

- **All bot classes** (`EchoBot`, `LlmBot`, `ChatBot`, `SystemBot`, `ToolBot`, `ReadBot`, `ScanBot`, `ChangeBot`, `SendBot`, `AgentBot`, `GuardBot`, `ProjectBot`, `MemoryBot`, `RetryBot`, and M365/Workspace variants) must implement the new `on_message` signature.
- `ChatApp._history: list[ChatMessage]` replaced by `ChatApp._context: list[ContextItem]`.
- `chat-participant` spec updated; `llm-context-builder` spec remains deprecated (no requirements to update).
- Tests for bots currently asserting on `history` parameter must be updated.
