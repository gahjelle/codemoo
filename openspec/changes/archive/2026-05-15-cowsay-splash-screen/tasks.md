## 1. Extract setup logic from tui.py

- [x] 1.1 Add `async def _setup_for_launcher(bot: BotType, variant: str) -> SetupResult` to `tui.py`, extracting the setup logic from `_chat()` (everything up to but not including `ChatApp(...).run_async()`)
- [x] 1.2 Refactor `_chat()` to call `_setup_for_launcher()` internally so behaviour is unchanged
- [x] 1.3 Verify the refactor with `uv run codemoo list-bots` (non-blocking subcommand) and `uv run pytest`

## 2. Build SplashApp

- [x] 2.1 Create `src/codemoo/frontends/splash.py` with a `SplashApp(App)` class
- [x] 2.2 Implement the fixed-layout ASCII art render: terminal code window (┌─ agent_loop.py ─┐), thought-bubble dots, cow, tongue line (always reserved), title
- [x] 2.3 Add four reactive attributes: `_code_pos: int`, `_tail_frame: int`, `_cursor_visible: bool`, `_head_state: str`
- [x] 2.4 Wire typewriter timer (40ms): increment `_code_pos`, stop at end of snippet
- [x] 2.5 Wire cursor-blink timer (500ms): toggle `_cursor_visible`
- [x] 2.6 Wire tail-wiggle timer (600ms): toggle `_tail_frame` between 0 and 1
- [x] 2.7 Wire head-animation timer (~3000ms + jitter): cycle through `open → blink (150ms) → open`, and occasionally `open → blink → tongue (300ms) → open`
- [x] 2.8 Apply color scheme via Rich markup: blue keywords, green identifiers/cursor, pink tongue, dim dots/frame, bold-cyan title, dim-italic subtitle
- [x] 2.9 Implement `run_worker(thread=True)` that: lazy-imports tui, calls `asyncio.run(_setup_for_launcher(bot, variant))`, then calls `self.call_from_thread(self.exit, result)`
- [x] 2.10 Handle worker exception: on error exit with `None` so launcher falls through gracefully

## 3. Build launcher entry point

- [x] 3.1 Create `src/codemoo/frontends/launcher.py` with `def main()` (no heavy imports at module level)
- [x] 3.2 Parse `sys.argv` for `--bot` and `--variant` flags (pass-through strings; validation stays in tui.py)
- [x] 3.3 Instantiate `SplashApp(bot=bot, variant=variant)` and call `.run()`; capture the `SetupResult` return value
- [x] 3.4 If result is not `None`, call `ChatApp(...).run()` with the unpacked result (import `ChatApp` lazily here, after splash)
- [x] 3.5 If result is `None` (worker error), re-run via `tui.code_app()` / `tui.business_app()` so existing error handling takes over

## 4. Wire entry points

- [x] 4.1 Update `pyproject.toml`: change `codemoo`, `moo`, `collebra`, and `ebra` entry points to `codemoo.frontends.launcher:main`
- [x] 4.2 Leave `demoo` entry point unchanged at `codemoo.frontends.cli:app`
- [x] 4.3 Run `uv sync` to rebuild the entry-point scripts

## 5. Verify and polish

- [x] 5.1 Manual visual check: run `uv run codemoo`, confirm splash appears before ChatApp, then quit with Ctrl+Q
- [x] 5.2 Manual visual check: confirm splash auto-dismisses when loading completes and ChatApp opens normally, then quit with Ctrl+Q
- [x] 5.3 Confirm `uv run demoo llm "hello"` shows no splash
- [x] 5.4 Manual visual checks: `uv run codemoo --bot EchoBot` and `uv run codemoo select` still work, quit with Ctrl+Q each time
- [x] 5.5 Manual visual check: confirm all four animation layers are visible: typewriter, cursor blink, tail wiggle, eye blink + tongue

## 6. Code quality and docs

- [x] 6.1 Run `uv run ruff format src/ tests/`
- [x] 6.2 Run `uv run ruff check src/ tests/`
- [x] 6.3 Run `uv run ty check src/ tests/`
- [x] 6.4 Run `uv run pytest`
- [x] 6.5 Review `AGENTS.md` and update the entry-point section if it documents the `tui:code_app` path
