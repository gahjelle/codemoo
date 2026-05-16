"""ChatBubble widget for displaying a single chat message."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Markdown, Static


class _BubbleContent(Widget):
    """Inner widget holding the header and Markdown body of a chat bubble."""

    DEFAULT_CSS = """
    _BubbleContent {
        height: auto;
        width: 80%;
    }
    """

    def __init__(
        self,
        name: str,
        emoji: str,
        text: str,
        thinking_time: int | None,
        css_class: str,
    ) -> None:
        super().__init__(classes=css_class)
        self._sender_name = name
        self._sender_emoji = emoji
        self._text = text
        self._thinking_time = thinking_time

    def compose(self) -> ComposeResult:
        """Yield a header label and a body widget appropriate to the bubble type."""
        header = f"{self._sender_emoji} [bold]{self._sender_name}[/bold]"
        if self._thinking_time is not None:
            header += f" [dim]({self._thinking_time}s)[/dim]"
        yield Label(header, classes="bubble-header", markup=True)
        if "bubble--commentator" in self.classes:
            yield Static(self._text, markup=True)
        else:
            yield Markdown(self._text)


class ChatBubble(Widget):
    """A full-width row containing a styled chat bubble.

    Human messages are right-aligned via CSS (align-horizontal: right on
    the bubble--human class). Bot messages are left-aligned by default.

    Fractional widths (80%) on _BubbleContent handle the split at any terminal
    width. Structural layout (height) is defined in DEFAULT_CSS; visual styling
    (colors, borders, spacing, alignment) lives in the external TCSS stylesheet.
    """

    DEFAULT_CSS = """
    ChatBubble {
        height: auto;
    }
    """

    def __init__(
        self,
        name: str,
        emoji: str,
        text: str,
        *,
        thinking_time: int | None = None,
        css_class: str,
    ) -> None:
        """Initialise the bubble with sender info and message content."""
        super().__init__(classes=css_class)
        self._sender_name = name
        self._sender_emoji = emoji
        self._text = text
        self._thinking_time = thinking_time
        self._css_class = css_class

    def compose(self) -> ComposeResult:
        """Yield the content widget; CSS handles alignment."""
        yield _BubbleContent(
            self._sender_name,
            self._sender_emoji,
            self._text,
            self._thinking_time,
            self._css_class,
        )
