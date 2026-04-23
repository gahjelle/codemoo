## 1. Fix empty follow-up reply in GeneralToolBot

- [x] 1.1 In `src/codemoo/core/bots/general_tool_bot.py`, guard the follow-up `complete` result: replace `text = await self.backend.complete(follow_up)` with `text = await self.backend.complete(follow_up) or "(tool executed, process interrupted)"`
- [x] 1.2 Add a unit test: when `backend.complete` returns `""`, `GeneralToolBot.on_message` returns a `ChatMessage` with text `"(tool executed, process interrupted)"`

## 2. Fix asyncio event loop in demo mode

- [x] 2.1 In `src/codemoo/frontends/tui.py`, extract the demo loop body into an `async def _run_demo(start: str | None = None) -> None` coroutine that uses `await ChatApp(...).run_async()` instead of `ChatApp(...).run()`
- [x] 2.2 Replace the body of `demo()` with a single `asyncio.run(_run_demo(start))` call and add the required `import asyncio`
- [x] 2.3 Verify manually: run `uv run codemoo demo`, send a message, press Ctrl-N, send a message to the next bot — it should succeed on the first attempt

## 3. Validation

- [x] 3.1 `uv run pytest` — all tests pass
- [x] 3.2 `uv run ruff check .` — no lint errors
- [x] 3.3 `uv run ruff format --check .` — no formatting issues
- [x] 3.4 `uv run ty check` — no type errors
