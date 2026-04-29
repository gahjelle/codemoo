## Why

The `build_llm_context` helper obscures the core conceptual difference between `LlmBot` and `ChatBot` during demos: a viewer must mentally unfold a five-argument function call to understand that `ChatBot` simply prepends history to the same message list `LlmBot` constructs inline. Inlining context construction makes this jump immediately visible in the code.

## What Changes

- **BREAKING** Remove `build_llm_context` from `core/backend.py`
- **BREAKING** Remove `human_name` field from `ChatBot`, `SystemBot`, `AgentBot`, `GuardBot`, and `SingleTurnToolBot`
- **BREAKING** Remove `max_messages` field from the same bots
- **BREAKING** Remove `human_name` parameter from `make_bots` and `_make_bot` in `bots/__init__.py`
- Each bot's `on_message` constructs its `list[Message]` inline using the pattern `[*[Message(...) for m in history], Message(role="user", content=message.text)]`, with `Message(role="system", content=self.instructions)` prepended for bots that have instructions
- Other bots' messages in history are no longer filtered out — they map to `"user"` role instead of being excluded

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `llm-context-builder`: Spec removed — `build_llm_context` is deleted entirely; context is built inline in each bot
- `chat-bot`: Requirement changes — no longer delegates to `build_llm_context`; no longer filters third-party messages; no longer clips history; drops `human_name` and `max_messages` fields
- `system-bot`: Same requirement changes as `chat-bot`
- `agent-bot`: Same requirement changes; drops `human_name` and `max_messages`
- `guard-bot`: Same requirement changes; drops `human_name` and `max_messages`
- `single-turn-tool-bot`: Same requirement changes; drops `human_name` and `max_messages`

## Impact

- `src/codemoo/core/backend.py` — remove `build_llm_context`
- `src/codemoo/core/bots/chat_bot.py`, `system_bot.py`, `agent_bot.py`, `guard_bot.py`, `single_turn_tool_bot.py` — inline context construction, remove fields
- `src/codemoo/core/bots/__init__.py` — remove `human_name` from factory
- `src/codemoo/frontends/tui.py` — remove `human_name` from `make_bots` calls
- `tests/core/test_backend.py` — delete (tests removed function)
- `tests/core/bots/test_chat_bot.py`, `test_system_bot.py`, `test_agent_bot.py`, `test_guard_bot.py`, `test_make_bots.py` — update for removed fields and changed filtering behaviour

## Non-goals

- Context window management (clipping, summarisation) — deferred to a future dedicated bot
- Filtering history to relevant senders — removed for now; can be reintroduced later as a deliberate context-management feature
