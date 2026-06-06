# Context Architecture

The conversation moves through three layers:

1. **`list[ChatMessage]`** — UI/log concern; owned by `ChatApp`; never sent to the LLM.
2. **`list[ContextItem]`** — shapeable intermediate layer; owned by `ChatApp`; supports disabling, editing, summarising, and injecting items.
3. **`list[Message]`** — LLM wire format; derived on-demand by `build_context()`.

## Key Modules

- **`src/codemoo/core/context_items.py`** — `ContextItem`, `ItemMode` enum, all `ContextContent` frozen dataclasses (`UserMessageContent`, `AssistantMessageContent`, `ToolUseContent`, `InjectedContent`, `SystemContent`), and pure list operations (`add_item`, `replace_item`, `set_mode`, `set_edited`, `set_summary`, `inject_at`, `next_turn_id`).
- **`src/codemoo/core/context_builder.py`** — `build_context(items) -> list[Message]`: DISABLED items are skipped; EDITED/SUMMARY modes substitute text; `ToolUseContent` unrolls to an assistant message + a tool message; `role_override` applies to non-tool items.

## Ownership and Preconditions

`ChatApp` owns `self._chat_context: list[ContextItem]`. Bots receive the full list as read-only input via `on_message(context)` and return only the new items they produced.

The app appends the triggering `UserMessageContent` item to `_chat_context` **before** calling `on_message`, so `context[-1]` is always the triggering message — this is a load-bearing precondition that bots may rely on.

The app extends `_chat_context` with the bot's returned items after each turn. Bots are append-only — only the user (via a future UI modal) modifies existing items.

`ToolUseContent` wraps the tool call and result atomically so that disabling a tool use also suppresses its result, preventing orphaned tool-result messages.

## Textual Widget CSS

Widget CSS follows a structural/visual split:

- `DEFAULT_CSS` — properties the widget cannot function without (e.g. `height: auto`, `layout`, fractional widths). These travel with the widget class.
- External `.tcss` file — visual/thematic properties only (colors, borders, spacing).
