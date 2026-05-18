"""ContextStatus widget showing conversation statistics for capability-aware bots."""

from textual.widgets import Label

_KILO = 1000


def _format_tokens(count: int) -> str:
    if count >= _KILO:
        return f"~{count / _KILO:.1f}k tokens"
    return f"~{count} tokens"


class ContextStatus(Label):
    """A status bar that shows context statistics when context_management is active.

    Hidden until the first message is exchanged.
    Structural layout (height) is defined here; visual styling lives in chat.tcss.
    """

    DEFAULT_CSS = """
    ContextStatus {
        height: 1;
    }
    """

    def on_mount(self) -> None:  # noqa: D102
        self.display = False

    def update_context(self, message_count: int, token_count: int) -> None:
        """Update the displayed message and token counts and make the widget visible."""
        self.update(f"{message_count} messages · {_format_tokens(token_count)}")
        self.display = True
