## 1. Extend BackendStatus widget

- [x] 1.1 Change `BackendStatus` from a `Label` subclass to a `Widget` subclass that composes two child `Label` widgets: a left mode label and a right backend/model label
- [x] 1.2 Add `mode: ModeName` parameter to `BackendStatus.__init__`; render left label as `mode.title()`
- [x] 1.3 Update `DEFAULT_CSS` to set `layout: horizontal` alongside `height: 1` (remove `width: 1fr` — child labels handle sizing)
- [x] 1.4 Update `chat.tcss` `BackendStatus` rule: add `width: 1fr` back on the widget level; style the right label (`#backend-label`) as `text-align: right; width: 1fr` and the left label (`#mode-label`) as `width: auto`

## 2. Pass mode through ChatApp

- [x] 2.1 Add `mode: ModeName = "code"` parameter to `ChatApp.__init__`; store as `self._mode`
- [x] 2.2 In `ChatApp.on_mount`, call `self.add_class(f"mode-{self._mode}")`
- [x] 2.3 In `ChatApp.compose()`, pass `mode=self._mode` to `BackendStatus`

## 3. Add background tint CSS classes

- [x] 3.1 Add `.mode-code` selector to `chat.tcss` with a dark purple-tinted background (e.g. `background: #130f1a`)
- [x] 3.2 Add `.mode-business` selector to `chat.tcss` with a dark green-tinted background (e.g. `background: #0f1a0f`)

## 4. Wire mode into all ChatApp call sites

- [x] 4.1 In `tui.py` `_chat()`, pass `mode=mode` to `ChatApp(...)`
- [x] 4.2 In `tui.py` `_select()`, pass `mode=mode` to `ChatApp(...)`
- [x] 4.3 In `tui.py` `_run_demo()`, pass `mode=mode` to `ChatApp(...)`

## 5. Verification

- [x] 5.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 5.2 Run `uv run ty check src/ tests/`
- [x] 5.3 Run `uv run pytest` and confirm all tests pass
- [x] 5.4 Review `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md`; update any documentation that references `BackendStatus` or `ChatApp` constructor signature if necessary
