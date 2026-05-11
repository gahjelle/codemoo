"""Multiline chat input widget."""

from dataclasses import dataclass

from textual.events import Key
from textual.message import Message
from textual.widgets import TextArea


class ChatInput(TextArea):
    """A multiline chat input that auto-grows (1-4 rows) and submits on Enter."""

    _MIN_LINES = 1
    _MAX_LINES = 4
    # border: tall adds one row top + one row bottom
    _BORDER_ROWS = 2

    @dataclass
    class Submitted(Message):
        """Posted when the user presses Enter with non-empty text."""

        chat_input: "ChatInput"
        value: str

        @property
        def control(self) -> "ChatInput":
            """The ChatInput that sent this message."""
            return self.chat_input

    def on_mount(self) -> None:
        """Set initial height to one content row plus border overhead."""
        self.styles.height = self._MIN_LINES + self._BORDER_ROWS

    async def _on_key(self, event: Key) -> None:
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            text = self.text.strip()
            if text:
                self.post_message(self.Submitted(self, text))
                self.clear()
        elif event.key == "alt+n":
            event.prevent_default()
            event.stop()
            self.insert("\n")

    def on_text_area_changed(self, _event: TextArea.Changed) -> None:
        """Grow or shrink the widget height as lines are added or removed."""
        line_count = self.text.count("\n") + 1
        content_lines = max(self._MIN_LINES, min(self._MAX_LINES, line_count))
        self.styles.height = content_lines + self._BORDER_ROWS
