# Spec: context-inspector

## Purpose

TBD — defines `ContextInspectModal`, a read-only Textual `ModalScreen` that displays a scrollable list of all `ContextItem`s in the current conversation, with per-item one-liner formatting, turn-group separators, and a header showing item count and token estimate. Opened via Ctrl-X when the `context_display` capability is active.

## Requirements

### Requirement: ContextInspectModal displays a scrollable read-only list of all ContextItems
`ContextInspectModal` SHALL be a `ModalScreen` that receives a snapshot of `list[ContextItem]` and a pre-calculated token count at construction time. It SHALL display one formatted row per item in a `VerticalScroll` body, ordered first-to-last (oldest at top, newest at bottom). The modal SHALL be read-only — no item selection, editing, or deletion.

#### Scenario: Modal opens with items in chronological order
- **WHEN** `ContextInspectModal` is pushed with a context of N items
- **THEN** the modal SHALL render N rows with the first item at the top and the last at the bottom

#### Scenario: Modal is scrollable when items exceed visible height
- **WHEN** the context contains more items than fit in the visible modal area
- **THEN** the user SHALL be able to scroll through all items using keyboard or mouse

#### Scenario: Modal is dismissed by Escape
- **WHEN** the user presses Escape while the modal is open
- **THEN** the modal SHALL dismiss and return focus to the main chat interface

### Requirement: Each ContextItem row uses a fixed-column one-liner format
Each row SHALL follow the format `{glyph}  {type:<4}  {preview}` where:
- `{glyph}` is a single Unicode character encoding the item's `ItemMode`
- `{type:<4}` is a 4-character left-aligned tag encoding the `ContextContent` type
- `{preview}` is truncated content text with no type-redundant prefix

Mode glyphs SHALL be: `▶` for ORIGINAL, `✎` for EDITED, `≈` for SUMMARY, `✗` for DISABLED.

Type tags SHALL be: `user` for `UserMessageContent`, `bot ` for `AssistantMessageContent`, `tool` for `ToolUseContent`, `sys ` for `SystemContent`, `inj ` for `InjectedContent`.

#### Scenario: ORIGINAL UserMessageContent row format
- **WHEN** a `ContextItem` has `mode=ORIGINAL`, `content=UserMessageContent(text="Hello world")`
- **THEN** its row SHALL start with `▶  user  Hello world`

#### Scenario: DISABLED ToolUseContent row format
- **WHEN** a `ContextItem` has `mode=DISABLED`, `content=ToolUseContent(name="read_file", ...)`
- **THEN** its row SHALL start with `✗  tool  read_file(`

#### Scenario: SUMMARY AssistantMessageContent row format
- **WHEN** a `ContextItem` has `mode=SUMMARY`, `content=AssistantMessageContent(text="...")`
- **THEN** its row SHALL start with `≈  bot `

### Requirement: Pinned items display a 📌 indicator between the glyph and type tag
When a `ContextItem` has `pinned=True`, a `📌` emoji SHALL be inserted between the mode glyph and the type tag: `{glyph} 📌 {type:<4}  {preview}`. Unpinned items SHALL use spaces in that position to maintain approximate column alignment.

#### Scenario: Pinned item shows 📌 indicator
- **WHEN** a `ContextItem` has `pinned=True`
- **THEN** its row SHALL contain `📌` between the mode glyph and type tag

#### Scenario: Unpinned item has no 📌 indicator
- **WHEN** a `ContextItem` has `pinned=False`
- **THEN** its row SHALL NOT contain `📌`

### Requirement: ToolUseContent preview shows name, first argument, and truncated output
For `ToolUseContent` items, the preview SHALL be formatted as `{name}({first_key}="{val}") → {output[:25]}` where `first_key` and `val` are the first key-value pair from the parsed `arguments_json`. If `arguments_json` is empty or unparseable, the preview SHALL fall back to `{name}(...)`.

#### Scenario: ToolUseContent with parseable arguments
- **WHEN** a `ToolUseContent` has `name="read_file"` and `arguments_json='{"path": "greeter.py"}'`
- **THEN** its preview SHALL be `read_file(path="greeter.py") → {first 25 chars of output}`

#### Scenario: ToolUseContent with empty arguments
- **WHEN** a `ToolUseContent` has `name="get_datetime"` and `arguments_json='{}'`
- **THEN** its preview SHALL be `get_datetime(...)`

### Requirement: InjectedContent preview includes the label
For `InjectedContent` items, the preview SHALL be formatted as `[{label}] {text}` so the label (which is not encoded in the `inj ` type tag) remains visible.

#### Scenario: InjectedContent preview includes label
- **WHEN** a `ContextItem` has `content=InjectedContent(label="memory", text="User prefers...")`
- **THEN** its preview SHALL start with `[memory] User prefers...`

### Requirement: Turn-group separators appear between items with different turn_ids
A thin dim separator Label SHALL be inserted in the row list between any two adjacent items whose `turn_id` values differ. No separator SHALL appear before the first item or after the last item.

#### Scenario: Separator between turns
- **WHEN** item at index N has `turn_id=0` and item at index N+1 has `turn_id=1`
- **THEN** a separator row SHALL appear between them in the modal

#### Scenario: No separator within the same turn
- **WHEN** two adjacent items share the same `turn_id`
- **THEN** no separator SHALL appear between them

### Requirement: Modal header shows item count and token estimate
The modal header SHALL display the count of `ContextItem`s and the pre-calculated token estimate in the same format used by `ContextStatus`: `"N items · ~Xk tokens"` (≥1000) or `"N items · ~X tokens"` (<1000).

#### Scenario: Header reflects the snapshot counts
- **WHEN** the modal is opened with 8 items and a 2400-token estimate
- **THEN** the header SHALL display `"8 items · ~2.4k tokens"`

### Requirement: Modal width is 90% of the terminal width
`ContextInspectModal` SHALL set `width: 90%` in its CSS. Row content that exceeds this width SHALL be clipped naturally by the widget's render boundary.

#### Scenario: Modal does not span full terminal width
- **WHEN** the modal is open in a terminal wider than 80 columns
- **THEN** the modal container SHALL occupy 90% of the terminal width with margins on each side

### Requirement: Ctrl-X opens ContextInspectModal when context_display capability is active
`ChatApp.on_key` SHALL open `ContextInspectModal` when the `ctrl+x` key is pressed AND `"context_display"` is in `self._active_capabilities`. The modal SHALL receive a snapshot of `self._chat_context` and the last calculated token count. The shortcut SHALL work in both demo and non-demo mode.

#### Scenario: Ctrl-X opens modal when capability is active
- **WHEN** `"context_display"` is in `_active_capabilities` and the user presses Ctrl-X
- **THEN** `ContextInspectModal` SHALL be pushed onto the screen stack

#### Scenario: Ctrl-X is a no-op when capability is inactive
- **WHEN** `"context_display"` is NOT in `_active_capabilities` and the user presses Ctrl-X
- **THEN** nothing SHALL happen
