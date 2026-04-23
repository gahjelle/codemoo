## 1. Core: bot factory and resolver

- [x] 1.1 Add `make_bots(backend, human_name)` factory to `src/codemoo/core/bots/__init__.py` returning the full ordered bot list (EchoBot → ShellBot)
- [x] 1.2 Add `resolve_bot(spec, bots)` helper (1-based index, case-insensitive name, case-insensitive type name; raises `ValueError` on no match)
- [x] 1.3 Write unit tests for `resolve_bot` covering all three resolution paths, exact and mixed-case inputs, out-of-range index, and unknown spec

## 2. ChatApp: demo_position parameter and DemoHeader widget

- [x] 2.1 Create `src/codemoo/chat/demo_header.py` with a `DemoHeader(Label)` widget that displays `{emoji} {name} ({type})  •  {n} of {total}  •  Ctrl-N: next bot`
- [x] 2.2 Add `demo_position: tuple[int, int] | None = None` parameter to `ChatApp.__init__`; store as `self._demo_position`
- [x] 2.3 Update `ChatApp.compose()` to yield `DemoHeader` as the first widget when `demo_position` is set
- [x] 2.4 Add `ChatApp.on_key()` handler: calls `self.exit("next")` when key is `ctrl+n` and `self._demo_position` is not `None`
- [x] 2.5 Add CSS for `DemoHeader` in `chat.tcss` (structural height in `DEFAULT_CSS`, visual styling in `chat.tcss`)

## 3. Frontend: codemoo.frontends package

- [x] 3.1 Create `src/codemoo/frontends/__init__.py` (empty)
- [x] 3.2 Create `src/codemoo/frontends/tui.py` with a module-level `app = cyclopts.App()` and three commands:
  - `@app.default` — `chat(*, bot: str | None = None)`: resolves bot (or uses last), launches `ChatApp`
  - `@app.command` — `select()`: launches `SelectionApp` then `ChatApp`
  - `@app.command` — `demo(*, start: str | None = None)`: outer loop advancing through bots via `ChatApp.exit("next")`
- [x] 3.3 Create `src/codemoo/frontends/cli.py` by moving `codemoo/cli.py` content; create backend inside each command function (not at module level)

## 4. Wiring and cleanup

- [x] 4.1 Update `pyproject.toml`: `codemoo = "codemoo.frontends.tui:app"` and `demoo = "codemoo.frontends.cli:app"`
- [x] 4.2 Strip `src/codemoo/__init__.py` — remove `main()` and bot construction; keep only necessary re-exports if any
- [x] 4.3 Delete `src/codemoo/cli.py`
- [x] 4.4 Run `uv sync` and verify `uv run codemoo`, `uv run codemoo --bot Ash`, `uv run codemoo select`, `uv run codemoo demo`, and `uv run demoo` all launch correctly

## 5. Tests

- [x] 5.1 Add tests for `DemoHeader` rendering (correct text for given bot + position tuple)
- [x] 5.2 Add `ChatApp` test: `demo_position=None` → no `DemoHeader` in widget tree, Ctrl-N has no effect
- [x] 5.3 Add `ChatApp` test: `demo_position=(1, 8)` → `DemoHeader` present, Ctrl-N returns `"next"`
- [x] 5.4 Add integration test for `make_bots()`: returns list in correct order with correct names and types

## 6. Validation

- [x] 6.1 Run `uv run pytest` — all tests pass
- [x] 6.2 Run `uv run ruff check .` — no lint errors
- [x] 6.3 Run `uv run ruff format --check .` — no formatting issues
- [x] 6.4 Run `uv run ty check` — no type errors
