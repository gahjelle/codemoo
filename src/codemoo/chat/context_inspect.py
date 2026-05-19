"""Read-only modal listing all ContextItems in the current session context."""

import json

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Label

from codemoo.chat.context_status import _format_tokens
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    InjectedContent,
    ItemMode,
    SystemContent,
    ToolUseContent,
    UserMessageContent,
)

_MODE_GLYPH: dict[ItemMode, str] = {
    ItemMode.ORIGINAL: "\N{BLACK RIGHT-POINTING TRIANGLE}",
    ItemMode.EDITED: "\N{PENCIL}",
    ItemMode.SUMMARY: "\N{ALMOST EQUAL TO}",
    ItemMode.DISABLED: "\N{MULTIPLICATION X}",
}

_TYPE_TAG: dict[type, str] = {
    UserMessageContent: "user",
    AssistantMessageContent: "bot ",
    ToolUseContent: "tool",
    SystemContent: "sys ",
    InjectedContent: "inj ",
}


def _preview(item: ContextItem) -> str:
    content = item.content
    if isinstance(content, ToolUseContent):
        try:
            args = json.loads(content.arguments_json)
            if args:
                key, val = next(iter(args.items()))
                arg_str = f'{key}="{val}"'
            else:
                arg_str = "..."
        except (json.JSONDecodeError, StopIteration):
            arg_str = "..."
        output_preview = content.output[:150]
        text = f"{content.name}({arg_str}) \N{RIGHTWARDS ARROW} {output_preview}"
    elif isinstance(content, InjectedContent):
        text = f"[{content.label}] {content.text}"
    else:
        text = content.text  # type: ignore[union-attr]
    return text.replace("\n", " ")


def _format_row(item: ContextItem) -> str:
    glyph = _MODE_GLYPH[item.mode]
    tag = _TYPE_TAG[type(item.content)]
    pin = " \N{PUSHPIN}" if item.pinned else "  "
    return f"{glyph}{pin} {tag}  {_preview(item)}"


class ContextInspectModal(ModalScreen[None]):
    """Read-only modal showing all ContextItems as scrollable one-liners."""

    DEFAULT_CSS = """
    ContextInspectModal {
        align: center middle;
    }
    """

    def __init__(self, items: list[ContextItem], token_count: int) -> None:
        """Initialise with a snapshot of the current context and its token count."""
        super().__init__()
        self._items = items
        self._token_count = token_count

    def compose(self) -> ComposeResult:
        """Yield the modal container with header and scrollable item list."""
        n = len(self._items)
        tokens = _format_tokens(self._token_count)
        with Vertical(id="context-inspect-container"):
            yield Label(
                f"{n} items \N{MIDDLE DOT} {tokens}",
                id="context-inspect-header",
            )
            with VerticalScroll(id="context-inspect-body"):
                prev_turn: int | None = None
                for item in self._items:
                    if prev_turn is not None and item.turn_id != prev_turn:
                        yield Label(
                            "\N{BOX DRAWINGS LIGHT HORIZONTAL}" * 4,
                            classes="context-inspect-separator",
                        )
                    yield Label(_format_row(item))
                    prev_turn = item.turn_id

    def on_mount(self) -> None:
        """Scroll to the bottom so the most recent items are visible on open."""
        self.query_one("#context-inspect-body", VerticalScroll).scroll_end(
            animate=False
        )

    def on_key(self, event: Key) -> None:
        """Dismiss on Escape."""
        if event.key == "escape":
            self.dismiss()
