## Context

The current chat input is Textual's built-in `Input` widget — a single-line field. It handles horizontal scrolling for long text but cannot render newlines, so multiline pastes (Ctrl-V or Ctrl-E demo prompts) either silently strip newlines or produce visual corruption.

Textual 8.x provides `TextArea`, a full multi-line editor widget. The challenge is that `TextArea`'s defaults (Enter inserts newline, no submit event, fixed height) need adapting for a chat-input UX.

## Goals / Non-Goals

**Goals:**
- Multiline text input with correct paste behaviour
- Auto-growing height (1–4 rows) so the input doesn't dominate the screen
- Ctrl+Enter to submit; Enter to insert newline
- Minimal changes outside `src/codemoo/chat/`

**Non-Goals:**
- Keyboard fallback for terminals that cannot distinguish Ctrl+Enter from Enter
- Rich editing features (syntax highlight, undo history beyond TextArea defaults)
- Persistent input history

## Decisions

### Subclass TextArea rather than compose around it

`ChatInput(TextArea)` keeps the widget self-contained: it owns its submit event, height management, and key overrides. An alternative wrapper-widget approach (a `Widget` containing a `TextArea`) would require proxying focus, value access, and events — more indirection for no benefit.

### Ctrl+Enter to submit; Enter for newline

This reversal of the single-line convention was chosen because:
1. It requires no key-default override — Enter already inserts `\n` in `TextArea`.
2. Only `ctrl+enter` needs interception (`_on_key` + `event.prevent_default()`).

Alternative considered: Enter submits, Shift+Enter for newline. Rejected because it requires preventing TextArea's default Enter behaviour and remapping Shift+Enter, which is more fragile.

Known risk: `ctrl+enter` is indistinguishable from `enter` in terminals without the Kitty keyboard protocol. Deferred to post-release.

### Dynamic height via `styles.height` on `Changed`

On every `TextArea.Changed` event, `ChatInput` counts newlines in `self.text` and sets `self.styles.height = clamp(line_count, 1, 4)`. This is the lightest available approach — no layout workers, no reactive properties. TextArea handles scrolling naturally when content exceeds 4 rows.

Alternative considered: fixed 3-row height. Rejected because a single-line prompt would waste space on most interactions.

### `ChatInput.Submitted` mirrors `Input.Submitted`

A typed `Message` subclass with a `value: str` field keeps `ChatApp` decoupled from `TextArea` internals. The handler signature in `ChatApp` stays nearly identical (`on_chat_input_submitted` vs `on_input_submitted`).

## Risks / Trade-offs

- **Ctrl+Enter terminal support** → Mitigation: document the limitation; revisit after first demo run in affected terminal
- **TextArea visual chrome differs from Input** → Mitigation: use `compact=True`, disable cursor-line highlight and line numbers; fine-tune CSS in `.tcss`
- **`load_text()` may not trigger `Changed`** → Mitigation: verify during implementation; if not, call height update explicitly after setting text

## Open Questions

- Does `TextArea.load_text()` fire a `Changed` event? (Verify in implementation — affects auto-grow when Ctrl-E inserts a prompt.)
