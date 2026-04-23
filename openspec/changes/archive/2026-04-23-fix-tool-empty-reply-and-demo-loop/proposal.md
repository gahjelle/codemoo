## Why

Two runtime bugs degrade the demo experience: `GeneralToolBot` can corrupt conversation history after a tool call, causing all subsequent LLM calls to fail with a 400 error; and switching bots via Ctrl-N in demo mode kills the asyncio event loop, making the first message to the next bot always fail.

## What Changes

- `GeneralToolBot.on_message`: guard the follow-up `complete` call so an empty string response is replaced with `"(tool executed, process interrupted)"` before being stored in history.
- `demo()` in `tui.py`: replace the `ChatApp(...).run()` loop with a single `asyncio.run()` at the outer level and `ChatApp(...).run_async()` inside, so the same event loop is reused across bot transitions.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `general-tool-bot`: Empty-string follow-up replies must never be stored in history; a non-empty fallback must be used instead.
- `demo-mode`: Switching to the next bot via Ctrl-N must not invalidate the shared asyncio event loop; the first user message after a bot switch must succeed.

## Impact

- `src/codemoo/core/bots/general_tool_bot.py` — one-line guard on the `complete` result.
- `src/codemoo/frontends/tui.py` — refactor `demo()` to use `asyncio.run` + `run_async`.
- No API, protocol, or dependency changes; no other bots affected.
