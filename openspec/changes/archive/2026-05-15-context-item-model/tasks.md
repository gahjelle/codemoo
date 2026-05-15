## 1. Core Types

- [x] 1.1 Create `src/codemoo/core/context.py` with `ContextContent` discriminated union, `ItemMode` enum, and `ContextItem` frozen dataclass (all fields: id, content, turn_id, mode, edited, summary, role_override, pinned)
- [x] 1.2 Add pure list operations to `context.py`: `next_turn_id`, `add_item`, `replace_item`, `set_mode`, `set_edited`, `set_summary`, `inject_at`
- [x] 1.3 Create `src/codemoo/core/context_builder.py` with `build_context(items: list[ContextItem]) -> list[Message]` — handles DISABLED/EDITED/SUMMARY modes, ToolUseContent unrolling, role_override, and natural role mapping

## 2. Protocol Update

- [x] 2.1 Update `ChatParticipant` protocol in `src/codemoo/core/participant.py`: `on_message` signature becomes `(message: ChatMessage, context: list[ContextItem]) -> tuple[ChatMessage | None, list[ContextItem]]`
- [x] 2.2 Update `HumanParticipant.on_message` to match the new signature (returns `(None, context)`)

## 3. Simple Bots

- [x] 3.1 Update `EchoBot.on_message`: accept context (ignore it), return one `AssistantMessageContent` item
- [x] 3.2 Update `LlmBot.on_message`: same shape as EchoBot; ignore context for LLM call, return one `AssistantMessageContent` item
- [x] 3.3 Update `ChatBot.on_message`: use `build_context(context)` to construct LLM input; return one `AssistantMessageContent` item (same shape as above)
- [x] 3.4 Update `SystemBot.on_message`: same pattern as ChatBot

## 4. Tool Bots

- [x] 4.1 Update `SingleTurnToolBot.on_message`: use `build_context(context)` for LLM call; return `[ContextItem(ToolUseContent), ContextItem(AssistantMessageContent)]` (or just the reply item if no tool was called)
- [x] 4.2 Update `AgentBot.on_message`: internal loop stays as local `list[Message]`; after loop completes return `[ContextItem(ToolUseContent) × N, ContextItem(AssistantMessageContent)]`
- [x] 4.3 Update `GuardBot.on_message` to new signature; return `[ContextItem(ToolUseContent) × N, ContextItem(AssistantMessageContent)]`
- [x] 4.4 Update `ProjectBot.on_message` to new signature; same return shape as GuardBot
- [x] 4.5 Update `MemoryBot.on_message` to new signature; same return shape
- [x] 4.6 Update `RetryBot.on_message` to new signature; same return shape

## 5. SingleTurnToolBot Subclasses

- [x] 5.1 Verify `ToolBot`, `ReadBot`, `ScanBot`, `ChangeBot`, `SendBot` work via updated `SingleTurnToolBot` base; fix any that override `on_message` directly
- [x] 5.2 Check `CommentatorBot` and `ErrorBot` for any `on_message` usage and update if needed

## 6. ChatApp Update

- [x] 6.1 Replace `_history: list[ChatMessage]` with `_context: list[ContextItem]` in `ChatApp.__init__`
- [x] 6.2 Update `on_chat_input_submitted`: append a `ContextItem(UserMessageContent(text))` to `self._context` when the user submits a message, before dispatching
- [x] 6.3 Update `_collect_replies`: pass current `self._context` into each `on_message` call and append returned new items to `self._context` after each call
- [x] 6.4 Update `_restart_bot`: reset `self._context` to `[]`

## 7. Tests

- [x] 7.1 Add unit tests for `ContextItem` construction and field defaults
- [x] 7.2 Add unit tests for all pure context operations (`next_turn_id`, `add_item`, `set_mode`, etc.)
- [x] 7.3 Add unit tests for `build_context`: DISABLED exclusion, EDITED/SUMMARY substitution, ToolUseContent unrolling, role_override, natural role mapping
- [x] 7.4 Update existing bot tests to pass `context=[]` and assert on the returned `(reply, context)` tuple
- [x] 7.5 Update `ChatApp` / dispatch tests for the new context threading behaviour

## 8. Documentation and Verification

- [x] 8.1 Read `AGENTS.md` and update Tools Architecture section to reference `context.py` and `context_builder.py`
- [x] 8.2 Run `uv run ruff format src/ tests/`
- [x] 8.3 Run `uv run ruff check src/ tests/`
- [x] 8.4 Run `uv run ty check src/`
- [x] 8.5 Run `uv run pytest`
