## Why

When running Codemoo in different modes (code vs. business), the TUI gives no visual indication of which mode is active. Users switching between `codemoo` and `enterproose` entry points have no at-a-glance confirmation of their context.

## What Changes

- The `BackendStatus` footer bar gains a mode label in the bottom-left corner (title-cased mode name, e.g. "Code", "Business"), while the existing backend/model text remains right-aligned.
- `ChatApp` gains a `mode` parameter so the UI can reflect the active mode.
- The app background receives a subtle per-mode color tint: purple for code mode, green for business mode. The general dark background is preserved.
- All call sites that construct `ChatApp` (`_chat`, `_select`, `_run_demo`) pass `mode` through.

## Non-goals

- No mode-switching at runtime; the mode is fixed at launch.
- No per-mode color changes to chat bubbles or other widgets.
- No changes to the CLI interface or mode names.
- No visual hints in the `SelectionApp` or demo slide overlay.

## Capabilities

### New Capabilities

- `mode-status-bar`: Mode label displayed in the bottom-left of the `BackendStatus` footer, alongside the existing backend/model text.
- `mode-background-tint`: App background carries a subtle color tint derived from the active mode.

### Modified Capabilities

- `backend-status-bar`: `BackendStatus` widget now also displays the active mode name; `ChatApp` accepts a `mode` parameter.

## Impact

- `src/codemoo/chat/backend_status.py` — `BackendStatus` receives `mode` and renders it left-aligned alongside the right-aligned backend/model text.
- `src/codemoo/chat/app.py` — `ChatApp.__init__` gains a `mode: ModeName` parameter; `compose()` passes `mode` to `BackendStatus` and applies a mode-derived CSS class to the app for background tinting.
- `src/codemoo/chat/chat.tcss` — adds per-mode CSS classes for background tint and updated `BackendStatus` layout rules.
- `src/codemoo/frontends/tui.py` — `_chat()`, `_select()`, and `_run_demo()` pass `mode` to `ChatApp`.
