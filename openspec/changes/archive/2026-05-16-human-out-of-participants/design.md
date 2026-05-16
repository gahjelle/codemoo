## Context

`HumanParticipant` currently satisfies `ChatParticipant` only because it must be in `_participants` for `ChatApp` to find its name and emoji. Its `on_message` returns `[]` on every call. Every bot reply dispatches to it and does nothing — the cost is small but the design is misleading: the protocol implies all participants receive and respond, but the human never does.

A separate issue: `ChatBubble` uses an `is_human: bool` parameter to choose between `[spacer | content]` and `[content | spacer]` layouts. Since `align-horizontal: right` is already used in `chat.tcss` and Textual supports it natively, this Python layout trick can be replaced with CSS and `is_human` eliminated from the widget layer too.

## Goals / Non-Goals

**Goals:**
- Remove `is_human` from `ChatParticipant`, `HumanParticipant`, all bot classes, `_sender_info`, and `ChatBubble`
- Make `HumanParticipant` a plain data container passed explicitly to `ChatApp`
- Replace Python spacer logic with a CSS alignment rule

**Non-Goals:**
- Changing how messages are composed or dispatched
- Modifying `_BubbleContent` visual styling
- Any changes to bot behaviour or LLM interaction

## Decisions

### 1. `human` as a required keyword argument to `ChatApp`

`ChatApp.__init__` gains `human: HumanParticipant` as an explicit argument; `participants` becomes bots-only. `_make_app` in tests and all `tui.py` call sites update accordingly.

Alternative considered: keep `HumanParticipant` in `participants` and just stop calling its `on_message`. Rejected — it still satisfies the protocol under false pretences and `is_human` would still be needed as a guard.

### 2. `_sender_info` tuple shrinks to `(emoji, css_class)`

The `is_human` bool in the tuple was only used to pass to `ChatBubble`. With `ChatBubble` dropping that parameter, the tuple can be simplified. The human's entry is added explicitly during `__init__` rather than via the participants loop.

### 3. CSS alignment replaces the Python spacer

`bubble--human` / `bubble--bot` move from `_BubbleContent` to the outer `ChatBubble` widget. `_BubbleContent` becomes purely structural (no CSS class). The stylesheet gains:

```css
ChatBubble.bubble--human {
    align-horizontal: right;
}
```

Visual rules (background, border, padding) already reference `.bubble--human`, `.bubble--bot` etc. — these now match `_BubbleContent`'s parent. Since `_BubbleContent` fills the bubble row, the background renders on the outer `ChatBubble`, which is the full-width row. This is equivalent to the previous behaviour and was verified to look correct.

`_BubbleContent` width changes from `4fr` (relative to a 5fr total with spacer) to `80%` (explicit, equivalent).

Alternative considered: keep the class on `_BubbleContent` and add an outer alignment class. Rejected — two classes for one logical "bubble type" adds indirection.

### 4. `HumanParticipant` becomes a plain dataclass

`on_message` and `is_human` are removed. The class no longer satisfies `ChatParticipant`; it is a plain data bag. No callers need it to satisfy the protocol.

## Risks / Trade-offs

- **Visual regression on bubble layout** → Mitigated by running `uv run codemoo` and visually confirming right-aligned human bubbles and left-aligned bot bubbles after the CSS change.
- **Test breakage** → All mocks in `test_collect_replies.py` carry `is_human`; all `test_bubble.py` tests use `is_human=True/False`. Both test files need updates alongside the source change.
- **`_make_app` helper in tests** → Currently passes `HumanParticipant()` in the participants list. After the change, it must pass `human=HumanParticipant()` separately.
