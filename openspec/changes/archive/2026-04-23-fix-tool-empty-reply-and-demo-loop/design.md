## Context

`GeneralToolBot` does one tool-call round-trip: it calls `complete_step` to get a tool request, executes the tool, then calls `complete(follow_up)` (without tools) to produce a final text reply. When the LLM "expected" to make multiple tool calls but can't (no tools are provided in the follow-up), it sometimes returns empty content. That empty string becomes `ChatMessage(text="")`, which `build_llm_context` later reconstructs as `Message(role="assistant", content="")` — a form Mistral rejects with HTTP 400.

The demo loop calls `ChatApp(...).run()` in a `while` loop. Textual's `.run()` wraps the app in `asyncio.run()`, creating and destroying a new event loop per iteration. The Mistral httpx client is shared across iterations; after the first loop closes, the client's connection pool references a dead loop. The first API call in the next iteration fails; subsequent calls recover silently.

## Goals / Non-Goals

**Goals:**
- Ensure `GeneralToolBot` never stores an empty-text `ChatMessage` in history.
- Ensure demo-mode bot transitions reuse a single asyncio event loop.

**Non-Goals:**
- Change the one-tool-call design of `GeneralToolBot` (that is intentional for the demo).
- Improve LLM behaviour to avoid empty responses (out of scope for this fix).
- Fix any other multi-tool or history management issues beyond the 400 error path.

## Decisions

### Bug 1 — Guard at the source, not the consumer

**Decision:** Add `or "(tool executed, process interrupted)"` to the `complete` result in `GeneralToolBot.on_message`, immediately before constructing `ChatMessage`.

**Alternatives considered:**

- *Filter in `build_llm_context`*: downstream patch; empty bot bubble already appeared to the user, and filtering can break the alternating user/assistant sequence.
- *`tool_choice="none"` in the backend*: architecturally correct but requires adding an optional parameter to the `LLMBackend` protocol, widening the interface for a single edge-case in one bot.

Guarding at the source is the minimal, targeted fix: one expression, one file, no interface changes.

### Bug 2 — Single event loop via `run_async`

**Decision:** Introduce an `async def _run_demo()` coroutine that calls `ChatApp(...).run_async()` in the while loop, and call it once with `asyncio.run(_run_demo())` in `demo()`.

**Alternatives considered:**

- *Call `_setup()` inside the loop*: creates fresh backends each iteration, which fixes the connection-pool problem but reinitialises random personas (ErrorBot, CommentatorBot) on every switch — inconsistent for a live demo.
- *Close the httpx client between iterations*: requires exposing a `close()` method on the backend, changing the `LLMBackend` protocol.

A single `asyncio.run` shell with `run_async` inside preserves all shared state and is the idiomatic Textual pattern for multi-app flows.

## Risks / Trade-offs

- **Visible fallback string**: `"(tool executed, process interrupted)"` will appear as a bot bubble when the LLM returns empty content. This is intentionally visible — it signals the partial-tool-call limitation to demo viewers rather than silently failing later.
- **`run_async` availability**: `App.run_async()` is part of Textual's public API since v0.1. No version risk.

## Migration Plan

Both changes are local and additive; no data migration, no deployment steps. Rolling back is a one-line revert per file.
