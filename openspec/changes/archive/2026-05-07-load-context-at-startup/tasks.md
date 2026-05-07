## 1. CommentatorBot — event buffering

- [x] 1.1 Change `_post_fn` field default in `__post_init__` from `lambda _: None` to `None` (type `Callable[[ChatMessage], None] | None`)
- [x] 1.2 Add `_pending: list[ChatMessage]` field (init=False, default_factory=list)
- [x] 1.3 In `_generate_comment`, replace direct `self._post_fn(msg)` call: if `_post_fn` is None append to `_pending`, else call `_post_fn`
- [x] 1.4 In `register()`, after setting `_post_fn`, flush `_pending` by calling `_post_fn` for each queued message and clearing the list

## 2. ProjectBot — startup protocol

- [x] 2.1 Replace `context_source: dict[str, str] | None` field with `context: str | None = None`
- [x] 2.2 Add `_context_source: dict[str, str] | None` as a separate init field (needed by `startup()` to know what to load)
- [x] 2.3 Add `async def startup() -> None` method that calls `read_project_context(self._context_source, ...)` and stores the result in `self.context`
- [x] 2.4 In `on_message`, replace the `await read_project_context(...)` block with direct use of `self.context`
- [x] 2.5 Remove the `if self.commentator is not None` guard around context loading in `on_message` (context is always pre-loaded; commentator check for tool events stays)

## 3. Bot factory — async make_bots with startup protocol

- [x] 3.1 Make `_make_bot` async; update the `ProjectBot` branch to pass `context_source=bot.context_source` (used by `startup()`) and `context=None` (populated by startup)
- [x] 3.2 Make `make_bots` async
- [x] 3.3 After constructing all bots, add a loop: `for bot in bots: if hasattr(bot, "startup"): await bot.startup()`

## 4. ChatApp — async on_mount

- [x] 4.1 Make `on_mount` async (`async def on_mount`)
- [x] 4.2 Move `commentator_bot.register(self._append_to_log)` call from `__init__` to `on_mount`

## 5. tui.py — async entry points

- [x] 5.1 Make `_setup` async; add `await` to `make_bots(...)` call
- [x] 5.2 Make `_chat` async; add `await` to `make_bots(...)` call
- [x] 5.3 Make `code_chat` and `business_chat` async (cyclopts runs async handlers natively)
- [x] 5.4 Check and update any other entry points in `tui.py` that call `_setup` or `make_bots`

## 6. Verification

- [x] 6.1 Run `uv run ruff format src/ tests/`
- [x] 6.2 Run `uv run ruff check src/ tests/`
- [x] 6.3 Run `uv run ty check src/ tests/`
- [x] 6.4 Run `uv run pytest`

## 7. Documentation

- [x] 7.1 Read `README.md`, `PLANS.md`, `AGENTS.md` and update any sections that reference ProjectBot context loading or bot construction
