## Why

The current single-line `Input` widget breaks when multiline text is pasted (via Ctrl-V or Ctrl-E demo prompts), producing UI glitches and mangled content. Replacing it with a growing `TextArea`-based widget eliminates these breakages and makes the input feel natural for longer prompts.

## What Changes

- **NEW**: `src/codemoo/chat/input.py` — `ChatInput` widget (subclass of `TextArea`) with auto-grow, Ctrl+Enter submit, and a custom `Submitted` message
- **MODIFIED**: `src/codemoo/chat/app.py` — swaps `Input` for `ChatInput`; updates event handler, query calls, and prompt insertion
- **MODIFIED**: `src/codemoo/chat/chat.tcss` — replaces `Input` styles with `ChatInput` styles

## Capabilities

### New Capabilities

- `chat-input`: A self-contained multiline chat input widget that auto-grows (1–4 rows), submits on Ctrl+Enter, accepts multiline paste, and fires a typed `Submitted` message

### Modified Capabilities

- `chat-ui`: The "Submit message with Enter key" requirement changes — Enter now inserts a newline; Ctrl+Enter submits

## Impact

- `src/codemoo/chat/input.py` — new file
- `src/codemoo/chat/app.py` — moderate changes (imports, event handler, query calls)
- `src/codemoo/chat/chat.tcss` — minor styling changes
- No changes to participants, bots, tools, or any other subsystem
- Ctrl+Enter may not be distinguishable from Enter in terminals that do not support the Kitty keyboard protocol; fallback strategy is deferred post-release

## Non-goals

- Keyboard shortcut fallback for terminals that cannot distinguish Ctrl+Enter from Enter
- Syntax highlighting or rich editing features in the input field
- Persistent input history or up-arrow recall
