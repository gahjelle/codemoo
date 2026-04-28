## Context

`ChatApp` launches in either code or business mode, but the TUI gives no visual feedback about which mode is active. The `BackendStatus` footer already exists as a `Label` widget that displays backend and model right-aligned. We need to extend it to carry the mode name and apply a per-mode background tint to the app.

## Goals / Non-Goals

**Goals:**
- Mode name visible in the bottom-left of the footer bar at all times
- Subtle per-mode background color on the app (purple for code, green for business)
- `ChatApp` receives `mode` and propagates it to the footer and to the body CSS class

**Non-Goals:**
- Runtime mode switching
- Color changes to chat bubbles, demo overlays, or selection screens
- New CLI flags or changes to how mode is determined

## Decisions

### BackendStatus layout: Widget with two Labels, not a styled single Label

**Chosen:** Change `BackendStatus` from `Label` to `Widget`, composing a left `Label` (mode name) and a right `Label` (backend + model).

**Rejected:** Keeping `BackendStatus` as a single `Label` and right-padding with spaces. This breaks on different terminal widths.

**Rationale:** A `Horizontal` widget with two flexing children is the idiomatic Textual pattern for split-side footer content. The structural `DEFAULT_CSS` sets `layout: horizontal` and `height: 1`; visual styling stays in `chat.tcss`.

### Background tint: CSS class on the App, not inline styles

**Chosen:** In `ChatApp.on_mount`, call `self.add_class(f"mode-{mode}")`. Define `.mode-code` and `.mode-business` selectors in `chat.tcss` that override `background`.

**Rejected:** Setting `styles.background` programmatically in Python. CSS classes keep visual logic in `.tcss` and make overrides trivial.

**Rationale:** This follows the project's structural/visual split convention — Python drives class state, CSS drives appearance. The tint needs to be subtle (hex background values close to Textual's default dark `$background`).

### Mode parameter on ChatApp: positional keyword with default "code"

**Chosen:** `mode: ModeName = "code"` added to `ChatApp.__init__`. All call sites in `tui.py` already have `mode` in scope and pass it through.

**Rationale:** Keeps the parameter optional so existing tests don't need changes (default matches the normal case). No new abstraction or wrapper needed.

## Risks / Trade-offs

- [Textual CSS class on App root] → The `.mode-code App` selector depth may interact with Textual's internal theme. Mitigation: use `ChatApp.mode-code` scoped selector or add class directly to the `App` and use `App.mode-code` in tcss.
- [BackendStatus refactor from Label to Widget] → Any test that asserts on `BackendStatus` as a `Label` type will need updating. Mitigation: tests check behavior (text content), not widget type.
- [Subtle tint contrast] → Very dark tints may be invisible on some terminals. Mitigation: choose hex colors with at least a 10% color component shift from neutral dark (`#121212`), e.g. `#130f1a` (code) and `#0f1a0f` (business).
