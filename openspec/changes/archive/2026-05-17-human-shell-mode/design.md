## Context

The TUI routes all user input through `on_chat_input_submitted` in `chat/app.py`, which builds a `ContextItem`, extends `_chat_context`, and dispatches to bots. Shell execution is available in `codemoo.core.tools.shell` as `_run_shell` (the implementation function) and `run_shell` (the `ToolDef` with metadata). The `ToolDef` carries a session-folder validator and `requires_approval=True` — both designed for LLM-initiated calls. The `ChatBubble` / `_BubbleContent` stack in `chat/bubble.py` renders either `Markdown` or `Static` depending on the sender class. Textual's `App.copy_to_clipboard()` writes via OSC 52.

## Goals / Non-Goals

**Goals:**
- `!`-prefixed input is intercepted before bots see it
- Shell output appears verbatim in a distinct bubble, clipboard-copied
- Verbatim rendering condition in `_BubbleContent` is named for its purpose

**Non-Goals:**
- Sandbox, path restriction, or approval for `!` commands
- Shell output injected into `_chat_context`
- Streaming, interactive commands, or shell history

## Decisions

### D1 — Intercept in `on_chat_input_submitted`, not in `ChatInput`

The `!` check belongs in `app.py`'s `on_chat_input_submitted`, not inside `ChatInput`. `ChatInput` is a pure input widget that knows nothing about routing. The app-level handler is the right seam: it already owns `_chat_context`, the sender registry, and `_append_to_log`.

**Alternative considered:** Intercept in `_on_key` inside `ChatInput`, posting a different message type. Rejected — it leaks routing concerns into a display widget.

### D2 — Call `_run_shell` directly, bypass `ToolDef` machinery

Import `_run_shell` from `codemoo.core.tools.shell` and call it directly. The `ToolDef` dispatch path (`dispatch_tool`) runs the validator and checks `requires_approval` — both are LLM guards. For user-typed commands, neither applies.

**Alternative considered:** Call `run_shell.fn` (the `ToolDef`'s fn attribute, same underlying function). This works but imports a `ToolDef` for no reason. Direct import is cleaner.

**Alternative considered:** Reuse the full `dispatch_tool` path with a no-op validator. Rejected — it introduces a fake `ToolDef` call, adds commentator noise, and obscures intent.

### D3 — `bubble--verbatim` as the rendering discriminator in `_BubbleContent`

`_BubbleContent` currently branches on `"bubble--commentator" in self.classes` to render `Static` vs `Markdown`. Rename the condition to `"bubble--verbatim" in self.classes`. Both `bubble--commentator` and the new `bubble--shell` will carry this class alongside their own.

**Why:** The branch encodes a rendering intent ("render this verbatim"), not a participant identity. Naming it for what it does makes the widget self-documenting and open to new verbatim senders.

**Implication:** `ChatBubble` for commentator messages will pass both `bubble--commentator` and `bubble--verbatim` as CSS classes. The external TCSS handles color; `bubble--verbatim` handles rendering mode only.

### D4 — Shell sender registered at `ChatApp.__init__` via `_sender_info`

A fixed `"Shell"` entry is added to `_sender_info` with `("\N{COMPUTER}", "bubble--shell bubble--verbatim")`. This is consistent with how `ErrorBot` is registered — a hardcoded special-purpose sender, not a `ChatParticipant`. No new participant class is needed.

### D5 — Output runs synchronously in a worker

`on_chat_input_submitted` already uses `self.run_worker(...)` for bot dispatch. Shell execution (`_run_shell`) is blocking (subprocess). Call it inside `run_worker` so the UI stays responsive, using the same exclusive=False pattern as bot dispatch.

### D6 — Clipboard via `App.copy_to_clipboard()`

Use Textual's built-in method. On WSL2, OSC 52 support depends on the terminal emulator (Windows Terminal supports it; some others do not). No fallback via `clip.exe` or `xclip` — a silent no-op on unsupported terminals is acceptable.

## Risks / Trade-offs

- **OSC 52 clipboard on WSL2** → On terminals that don't support OSC 52, clipboard copy silently does nothing. Mitigation: acceptable for now; no fallback in scope.
- **Blocking shell in worker thread** → Long-running commands (e.g., `! sleep 60`) block the worker thread. Mitigation: `_run_shell` has a 30s timeout built in; the UI remains interactive via the worker model.
- **`bubble--verbatim` on commentator bubbles** → Adding a second CSS class to existing commentator bubbles is a visual no-op (TCSS targets `bubble--commentator` for color), but it's a subtle change to the class set. Mitigation: low risk; class addition is additive and TCSS selectors are explicit.
