## Context

The chat UI is a Textual TUI app. Messages are currently appended to a `RichLog` widget as plain Rich markup strings (`[bold]name[/bold]: text`). All participants look identical. The `ChatParticipant` protocol has only `name` and `on_message`.

Textual supports external CSS via `.tcss` files, custom `Widget` subclasses, and Rich's `Markdown` widget for Markdown rendering. Styles can be applied per CSS class or ID.

## Goals / Non-Goals

**Goals:**
- Each participant has a unique emoji (part of the protocol)
- `HumanParticipant` has hardcoded defaults: name `"You"`, emoji `"🧑"`, color `#4a9eff`
- Message bubbles show emoji + name in bold at top, Markdown body below
- Bubble background color is keyed to the participant
- Human bubbles align right; all others align left
- All styles live in a `.tcss` file — no inline styles anywhere

**Non-Goals:**
- User-configurable emoji/name/color for the human participant
- Dynamic color assignment (colors are hardcoded per participant type for now)
- Persisting or theming the chat outside the TUI session

## Decisions

### Replace `RichLog` with a scrollable container of `ChatBubble` widgets

**Decision**: Replace the `RichLog` widget with a `VerticalScroll` (or `ScrollableContainer`) that we append `ChatBubble` widget instances to.

**Rationale**: `RichLog` only supports Rich markup strings — it cannot host arbitrary widget trees. Markdown rendering and per-bubble layout (alignment, padding, background) requires real widgets. `VerticalScroll` auto-scrolls and supports `mount()` for dynamic appending.

**Alternative considered**: Keep `RichLog` and encode everything as Rich markup. Rejected because Rich markup doesn't support true Markdown (code fences, lists, etc.) and can't do right-alignment via markup alone.

### `ChatBubble` is a `Static` widget containing a `Markdown` child

**Decision**: `ChatBubble` extends `Static` (or `Widget`) and renders the header line via its `compose()` method using a `Label` for the name/emoji and a `Markdown` widget for the body.

**Rationale**: Textual's `Markdown` widget handles full CommonMark rendering. Wrapping it in a container widget gives us a styling hook for the bubble background and border.

**Alternative considered**: Render everything as Rich `Text` inside a `Static`. Rejected because it doesn't support real Markdown.

### Participant color as a CSS class, not inline style

**Decision**: Assign each participant a stable CSS class (e.g., `bubble--human`, `bubble--bot`) derived from their role or name. The `.tcss` file defines the background color for each class.

**Rationale**: Inline styles are explicitly excluded. A CSS-class approach maps cleanly to Textual's styling model and keeps all visual decisions in one file.

**Alternative considered**: Use Textual's `styles` object at runtime (`widget.styles.background = ...`). Rejected because it is effectively inline styling in code.

### Human alignment via CSS `align` and `dock` on the bubble container

**Decision**: Human bubbles get a CSS class (e.g., `bubble--human`) that sets `align-horizontal: right` and a reasonable `margin-left` to push content right. Bot bubbles use default left alignment with `margin-right`.

**Rationale**: Textual's layout system handles alignment declaratively in TCSS; no Python geometry math needed.

### `emoji` added to `ChatParticipant` protocol

**Decision**: Add `emoji: str` as a required protocol property alongside `name`.

**Rationale**: The emoji is a display concern tied to identity — it belongs on the participant, not computed elsewhere. Protocol-level enforcement means all participants must declare one.

## Risks / Trade-offs

- **Markdown widget per bubble is heavier than RichLog lines** → Acceptable for a TUI with moderate message counts; revisit if performance degrades with hundreds of messages
- **CSS class per participant type is not fully dynamic** → A fixed set of classes (`bubble--human`, `bubble--bot`, `bubble--system`) covers current needs; a color-palette approach can be added later
- **`VerticalScroll` auto-scroll behavior** → Textual's `scroll_end()` must be called after mounting a new bubble; the existing `auto_scroll=True` pattern does not apply to container widgets

## Migration Plan

1. Update `ChatParticipant` protocol to require `emoji: str`
2. Add `emoji` to `HumanParticipant` and any existing bot participants (`EchoBot`)
3. Create `ChatBubble` widget and `chat.tcss` stylesheet
4. Wire stylesheet into `ChatApp.CSS_PATH`
5. Replace `RichLog` with `VerticalScroll` in `ChatApp.compose()`
6. Replace `_append_to_log` with `mount(ChatBubble(...))` call
7. Update tests

No migration of stored data — purely a UI change. Rollback: revert the above files.

## Open Questions

- Should `EchoBot` pick its emoji from a fixed constant or accept it as a constructor argument? (Lean toward constructor argument for flexibility.)
- Should the bubble CSS classes use participant `name` (sanitized) or a fixed type-based class? (Lean toward type-based for predictability.)
