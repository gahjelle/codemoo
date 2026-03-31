"""Textual TUI application wiring together chat participants."""

from collections.abc import Sequence
from datetime import UTC, datetime

from textual.app import App, ComposeResult
from textual.widgets import Input, RichLog

from gaia.chat.message import ChatMessage
from gaia.chat.participant import ChatParticipant


class ChatApp(App[None]):
    """Main TUI application that hosts the chat log and input widget."""

    def __init__(self, participants: Sequence[ChatParticipant]) -> None:
        """Initialise with an ordered list of chat participants."""
        super().__init__()
        self._participants = list(participants)

    def compose(self) -> ComposeResult:
        """Yield the scrollable log and the text input field."""
        yield RichLog(id="log", auto_scroll=True, markup=True)
        yield Input(placeholder="Type a message and press Enter...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter in the input box: create a message and dispatch it."""
        text = event.value.strip()
        # Empty input produces no message per spec
        if not text:
            return
        self.query_one(Input).clear()
        message = ChatMessage(
            sender="You",
            text=text,
            timestamp=datetime.now(tz=UTC),
        )
        self._append_to_log(message)
        # Dispatch in a worker so participant coroutines run without blocking the UI
        self.run_worker(self._dispatch(message), exclusive=False)

    def _append_to_log(self, message: ChatMessage) -> None:
        # RichLog with auto_scroll=True scrolls to latest entry automatically
        log = self.query_one(RichLog)
        log.write(f"[bold]{message.sender}[/bold]: {message.text}")

    async def _dispatch(self, initial_message: ChatMessage) -> None:
        """Propagate a message to all participants, then propagate any replies.

        Uses a queue to avoid recursion. The loop terminates naturally because
        bots are required to filter their own messages (returning None).
        """
        queue: list[ChatMessage] = [initial_message]
        while queue:
            message = queue.pop(0)
            for participant in self._participants:
                reply = await participant.on_message(message)
                if reply is not None:
                    self._append_to_log(reply)
                    queue.append(reply)
