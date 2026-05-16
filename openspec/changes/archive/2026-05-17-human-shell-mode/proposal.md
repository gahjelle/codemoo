## Why

The TUI has no way for the user to run a shell command and see the result without leaving the app. Adding a `!`-prefix shortcut — borrowed from the REPL and CLI tradition — lets users inspect files, check git status, or probe the environment mid-conversation and optionally paste the output into the next prompt.

## What Changes

- When a `ChatInput.Submitted` value starts with `!`, the app intercepts it before any bot machinery runs.
- The rest of the input is passed directly to `_run_shell` (no sandbox, no approval gate — the user is trusted).
- The output is displayed verbatim in a new **shell output bubble** (`bubble--shell` CSS class, "Shell" sender, 💻 emoji).
- The output is copied to the system clipboard via `App.copy_to_clipboard()`.
- The output is **not** added to `_chat_context`; the clipboard is the bridge if the user wants to inject it.
- The `_BubbleContent` verbatim-rendering branch is renamed from `bubble--commentator` to `bubble--verbatim` so its intent is explicit; `bubble--commentator` adopts this class alongside its own.

## Capabilities

### New Capabilities

- `human-shell-mode`: `!`-prefix interception in `on_chat_input_submitted` — routing, shell execution, output display, and clipboard copy.

### Modified Capabilities

- `chat-bubble-display`: adds `bubble--shell` CSS class and renames the verbatim rendering condition from `bubble--commentator` to `bubble--verbatim`.

## Non-goals

- Shell output does not enter `_chat_context` automatically; context injection remains a manual user action (paste from clipboard).
- No sandbox or path restriction on `!` commands; the session-folder validator is for LLM-initiated calls only.
- No approval gate for `!` commands.
- No shell history, tab completion, or interactive commands.
- No streaming of shell output; output appears when the command completes.
