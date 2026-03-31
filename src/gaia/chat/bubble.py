"""ChatBubble widget for displaying a single chat message."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Markdown, Static


class _BubbleContent(Widget):
    """Inner widget holding the header and Markdown body of a chat bubble."""

    DEFAULT_CSS = """
    _BubbleContent {
        height: auto;
    }
    """

    def __init__(self, name: str, emoji: str, text: str, css_class: str) -> None:
        super().__init__(classes=css_class)
        self._sender_name = name
        self._sender_emoji = emoji
        self._text = text

    def compose(self) -> ComposeResult:
        """Yield a header label and a Markdown body."""
        header = f"{self._sender_emoji} [bold]{self._sender_name}[/bold]"
        yield Label(header, classes="bubble-header", markup=True)
        yield Markdown(self._text)


class ChatBubble(Widget):
    """A full-width row containing a spacer and a styled chat bubble.

    Human messages are right-aligned: [spacer | content].
    Bot messages are left-aligned:    [content | spacer].

    Fractional widths (1fr / 4fr) handle the split at any terminal width,
    avoiding the need for percentage-based margins which Textual does not support.
    All visual styling is defined in the external TCSS stylesheet.
    """

    DEFAULT_CSS = """
    ChatBubble {
        height: auto;
        layout: horizontal;
    }
    """

    def __init__(self, name: str, emoji: str, text: str, *, is_human: bool) -> None:
        """Initialise the bubble with sender info and message content."""
        super().__init__()
        self._sender_name = name
        self._sender_emoji = emoji
        self._text = text
        self._is_human = is_human

    def compose(self) -> ComposeResult:
        """Yield spacer and content in the order that produces the correct alignment."""
        css_class = "bubble--human" if self._is_human else "bubble--bot"
        content = _BubbleContent(
            self._sender_name, self._sender_emoji, self._text, css_class
        )
        spacer = Static("", classes="bubble-spacer")
        if self._is_human:
            yield spacer
            yield content
        else:
            yield content
            yield spacer
