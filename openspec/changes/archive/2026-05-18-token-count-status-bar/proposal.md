## Why

The `context_management` status bar currently shows only a message count, which tells the user little about how close the session is to a context limit. Token count is the meaningful signal — both for users monitoring their session and as the future trigger for CompactBot's automatic compaction.

## What Changes

- Add `tiktoken` as a project dependency.
- Create `src/codemoo/core/token_counter.py` with a single `estimate_tokens(messages: list[Message]) -> int` function using the `cl100k_base` encoder (reasonable approximation for Claude's tokenizer).
- Update `ContextStatus` to display both message count and estimated token count, e.g. `12 messages · ~3.2k tokens`.
- Update the `ChatApp` call site to pass token count alongside the message count when refreshing `ContextStatus`.

## Non-goals

- Exact token counts for Claude (would require an Anthropic API call per turn).
- Showing token counts for backends other than the current session's messages.
- Any compaction logic — that belongs to CompactBot.

## Capabilities

### New Capabilities

- `token-counter`: Utility module that estimates token count from a `list[Message]` using tiktoken. Single module-level encoder instance; no network calls after first use.
- `context-status-bar`: The `ContextStatus` widget behaviour — displays message count and estimated token count for bots with the `context_management` capability.

### Modified Capabilities

*(none — `bot-capability-declarations` is unchanged; `context_management` stays as the capability name)*

## Impact

- **New dependency**: `tiktoken` (PyPI).
- **New file**: `src/codemoo/core/token_counter.py`.
- **Modified**: `src/codemoo/chat/context_status.py` — updated display and updated `update_message_count` signature (or new method).
- **Modified**: `src/codemoo/chat/app.py` — call site passes token estimate.
- **No protocol changes**: `ChatParticipant`, `LLMBackend`, and `ContextItem` are untouched.
