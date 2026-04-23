## Why

When a tool-enabled bot calls a tool, nothing visible happens — the user sees the bot thinking, then a final reply, with no insight into what happened in between. Adding commentary during tool calls makes the agentic loop legible and entertaining, and demonstrates how real coding agents work under the hood.

## What Changes

- **New**: `CommentatorBot` — a side-channel observer (not a `ChatParticipant`) that generates short LLM-powered asides when tools are invoked
- **New**: `ToolCallEvent` — a typed, frozen dataclass carrying `bot_name`, `tool_name`, and `arguments`; the first entry in an extensible commentary event protocol
- **New**: Four commentator personas (Arne, Herwich, Sølve, Rike) chosen randomly per comment, plus Streik as a hardcoded fallback when the LLM call fails
- **Modified**: `AgentBot` and `GeneralToolBot` gain an optional `commentator` field; they call `await commentator.comment(event)` before each tool invocation
- **Modified**: `ChatApp` accepts a `commentator_bot` alongside `error_bot`, registers it with a post callback, and uses a fallback path in `_append_to_log` for unrecognised sender names
- **Modified**: `ChatBubble` / CSS gets a new `bubble--commentator` class (softer, greyer) for commentary messages

## Capabilities

### New Capabilities

- `commentator-bot`: The `CommentatorBot` class — personas, LLM commentary, Streik fallback, and the `register` / `comment` API
- `commentary-events`: The typed event protocol (`ToolCallEvent`) that bots emit to trigger commentary, designed to extend to other event types in the future

### Modified Capabilities

- `chat-bubble-display`: New `bubble--commentator` CSS class and fallback sender-lookup path in `_append_to_log`

## Impact

- `src/codemoo/core/bots/agent_bot.py` — add optional `commentator` field and `comment()` call
- `src/codemoo/core/bots/general_tool_bot.py` — same
- `src/codemoo/core/bots/commentator_bot.py` — new file
- `src/codemoo/chat/app.py` — accept and wire `commentator_bot`; fallback path in `_append_to_log`
- `src/codemoo/chat/chat.tcss` — add `bubble--commentator` style rules
- `src/codemoo/frontends/tui.py` — construct and inject `CommentatorBot`
- No new dependencies; `CommentatorBot` uses the existing `LLMBackend` protocol
