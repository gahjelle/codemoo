## Context

Codemoo's chat loop (`_collect_replies` in `chat/app.py`) is a BFS async generator that sequentially awaits each participant's `on_message()`. LLM-backed participants can take several seconds to respond, with no UI feedback during that time. Any exception raised inside `on_message()` currently propagates uncaught through the worker, crashing the reply stream.

Two additions address this: a status bar that reflects which participant is currently awaiting a response, and an `ErrorBot` that intercepts exceptions and surfaces them as in-chat bubbles.

## Goals / Non-Goals

**Goals:**
- Show which bot is actively thinking via a status bar between the log and input
- Catch participant exceptions without crashing the loop; surface them as styled error bubbles
- ErrorBot reuses the existing Mistral backend to generate personality-flavored error messages, with a hard fallback to plain text when the LLM is unreachable
- ErrorBot randomly adopts one of three named personas at startup (Errol, Glitch, or Murphy), each with a distinct name, emoji, and LLM system prompt
- ErrorBot is always present (like `HumanParticipant`) — no user opt-in required

**Non-Goals:**
- Streaming token-by-token output (future work)
- Per-bot progress bars or typing indicators in the message log
- Retry logic for failed LLM calls

## Decisions

### Status bar as a Textual `Label` widget

A `Label` widget added between `VerticalScroll` and `Input` in `compose()` holds the status text. The dispatch loop sets it directly via `self.query_one(StatusBar).update(...)` before and after each `await participant.on_message()`.

Alternative considered: posting a custom Textual `Message` (e.g. `BotThinking`) and handling it in an `on_bot_thinking` handler. This would be cleaner in a larger app but adds indirection for a single-widget update; direct mutation is simpler here.

### ErrorBot as a message factory, not a dispatch participant

`ErrorBot` is instantiated and passed into `ChatApp` like any other participant, but its `on_message()` always returns `None` — it never responds to normal chat messages. Instead, the dispatch loop calls `error_bot.format_error(participant, exception)` directly when a try/except fires, and yields the resulting `ChatMessage`.

Alternative considered: injecting a synthetic "error event" message into the BFS queue and having ErrorBot respond to it. This keeps the loop uniform, but adds a message type that has no meaning outside error handling; the factory approach is simpler and more transparent.

### ErrorBot tries LLM first, falls back to plain text

`ErrorBot.format_error()` attempts a single LLM completion with a short, focused system prompt. If that call raises any exception, it returns a deterministic fallback string instead. The double-failure case (LLM down, ErrorBot also down) is handled gracefully without nesting try/except in the caller.

### Error messages are yielded to the log but not added to the BFS queue

In `_collect_replies`, normal replies are both yielded (→ displayed) and appended to the BFS queue (→ dispatched to other participants). Error messages must only be displayed. If an error message were queued, LLM bots would receive it and attempt to respond, which is not the intended behaviour.

The except branch therefore yields the error `ChatMessage` directly without appending it to `queue`. No new message type or flag is needed.

### ErrorBot is excluded from the participant skip-logic

`_collect_replies` skips dispatching a message back to its own sender (`message.sender == participant.name`). ErrorBot is in the participants list but is never a message sender from the loop's perspective (its messages originate from the except branch, not from `on_message()`). No special-casing needed.

### ErrorBot persona is chosen at instantiation via `random.choice`

Three `Persona` dataclasses (or a similar lightweight structure) each carry a `name`, `emoji`, and `system_prompt`. `ErrorBot.__init__` calls `random.choice(PERSONAS)` and stores the result. This keeps persona data co-located with the class and makes it trivial to add more personas later.

### Thinking status cleared in a `finally` block

The status bar update before `on_message()` and the clear after are wrapped in try/finally so the status bar never gets stuck showing "thinking" after an error.

```
before: status_bar.update(f"{p.emoji} {p.name} is thinking…")
try:
    reply = await p.on_message(...)
except Exception as e:
    yield error_bot.format_error(p, e)
finally:
    status_bar.update("")
```

## Risks / Trade-offs

- **ErrorBot LLM tone vs. failure clarity** — A witty LLM-generated message is more engaging but might obscure technical details. The plain fallback always includes the exception type and message, so diagnostic info is never lost.
- **Sequential bot processing** — The current loop awaits bots one at a time; the status bar only ever shows one active bot. This is correct behavior today but will need revisiting if bots are parallelised in the future.
- **Status bar visual weight** — A persistent empty widget adds a small layout gap when idle. CSS can collapse it to zero height when content is empty.
