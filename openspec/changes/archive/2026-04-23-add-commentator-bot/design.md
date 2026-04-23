## Context

Tool-enabled bots (`AgentBot`, `GeneralToolBot`) run tool calls inside `on_message`, which is opaque to the app. The dispatch loop in `ChatApp._collect_replies` only sees the finished `ChatMessage` returned at the end. There is no current mechanism for a bot to emit observations mid-turn.

`ErrorBot` establishes the pattern of a non-participant side-channel component that is wired into `ChatApp` alongside the participant list and speaks through a direct post function rather than through the BFS dispatch loop.

## Goals / Non-Goals

**Goals:**
- Commentary messages appear in the chat log before the tool result, while the bot is still thinking
- Commentary does not enter message history — it is display-only chrome
- The event protocol can be extended to non-tool-call events without changing call sites
- Personas are entertaining and distinct; the fallback path is always safe
- `CommentatorBot` is optional; bots without it work identically to today

**Non-Goals:**
- Commentary on tool *results* (post-call narration) — deferred
- Async tool execution — tools remain synchronous
- Multiple simultaneous commentators
- Configurable persona selection (always random per comment for now)

## Decisions

### CommentatorBot is not a ChatParticipant

`CommentatorBot` has no `on_message` and is not in the `_participants` list. It speaks by calling a registered post callback directly, bypassing `_collect_replies`. This matches how `ErrorBot` works and keeps commentary out of history and the dispatch loop.

**Alternatives considered:**
- *Generator protocol on `on_message`*: bots yield intermediate `ChatMessage` values. Cleaner per-bot but requires changing the shared protocol, breaks the CLI frontend symmetrically, and couples display concerns into agent logic.
- *Async queue drained between participant calls*: possible but adds timing complexity for no gain when commentary is fire-and-forget.

### Typed event protocol as the call-site interface

Bots call `await commentator.comment(event)` with a typed event object rather than passing raw `ToolUse` fields directly. This means:
- The `comment` signature never changes as new event types are added
- Call sites do not need updating when commentary is extended
- `ToolCallEvent` is a thin frozen dataclass in `commentator_bot.py` (no separate module needed at this scale)

**Alternatives considered:**
- *Pass `ToolUse` directly*: leaks backend internals into the commentary interface; `ToolUse` carries LLM-protocol fields (`call_id`, `assistant_message`) irrelevant to commentary.
- *String-only interface (`tool_name: str, args_str: str`)*: loses structure needed if future events carry richer data.

### Random persona per comment, not per session

Each `comment()` call draws a persona at random from the four main personas (Arne, Herwich, Sølve, Rike). This means a single long agent loop can cycle through multiple voices, making commentary feel like a booth rather than a single narrator.

**ErrorBot contrast:** ErrorBot picks at startup for session-level consistency; an error always comes from the same voice. Commentary is lighter and more varied — different semantics warrant different behaviour.

### Fallback sender "Streik" for LLM failures

When the LLM call raises, `comment()` catches the exception, emits a hardcoded log-style line as "Streik", and returns without re-raising. Commentary is non-critical; a failure here must never surface as an error or silence the main bot.

Streik's format: `{bot_name} calls {tool_name}({formatted_args})` — a bare function-call string, readable without any personality layer.

### Fallback sender-lookup in `_append_to_log`

`_sender_info` currently requires explicit registration of every sender name. Because the persona active at post time is chosen randomly, all five names (Arne, Herwich, Sølve, Rike, Streik) would need pre-registration. Instead, `_append_to_log` gains a fallback: if `message.sender` is not found in `_sender_info`, it uses `("💬", False, "bubble--commentator")`. This means new personas work automatically and `ChatApp` needs no change when personas are added or renamed.

## Risks / Trade-offs

- **Two-phase init on `CommentatorBot`**: constructed before `ChatApp`, post callback registered after. The object is unusable between construction and `register()`. Risk is low — `ChatApp.__init__` calls `register` immediately — but it is a mutable-state seam that tests must handle carefully (pass a no-op callback or call `register` before the test fires).
- **LLM latency per tool call**: each tool use triggers an extra LLM round-trip for the commentary. For demo / educational use this is acceptable. For production-speed agents it may not be.
- **Persona randomness in tests**: `random.choice` in the hot path makes exact sender name unpredictable. Tests for commentary content should either mock `random.choice` or assert on the CSS class rather than the sender name.
