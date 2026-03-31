"""Textual TUI application wiring together chat participants."""

from collections.abc import AsyncGenerator, Sequence
from datetime import UTC, datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input

from gaia.chat.bubble import ChatBubble
from gaia.core.message import ChatMessage
from gaia.core.participant import ChatParticipant


class ChatApp(App[None]):
    """Main TUI application that hosts the chat log and input widget."""

    CSS_PATH = Path(__file__).parent / "chat.tcss"

    def __init__(self, participants: Sequence[ChatParticipant]) -> None:
        """Initialise with an ordered list of chat participants."""
        super().__init__()
        self._participants = list(participants)
        # Build a lookup from sender name → (emoji, is_human) for bubble rendering
        self._sender_info: dict[str, tuple[str, bool]] = {
            p.name: (p.emoji, p.is_human) for p in participants
        }
        # Keep a reference to the human participant for outgoing message construction
        self._human = next(p for p in participants if p.is_human)

    def compose(self) -> ComposeResult:
        """Yield the scrollable log and the text input field."""
        yield VerticalScroll(id="log")
        yield Input(placeholder="Type a message and press Enter...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter in the input box: create a message and dispatch it."""
        text = event.value.strip()
        # Empty input produces no message per spec
        if not text:
            return
        self.query_one(Input).clear()
        message = ChatMessage(
            sender=self._human.name,
            text=text,
            timestamp=datetime.now(tz=UTC),
        )
        self._append_to_log(message)
        # Dispatch in a worker so participant coroutines run without blocking the UI
        self.run_worker(self._dispatch(message), exclusive=False)

    def _append_to_log(self, message: ChatMessage) -> None:
        default = ("\N{SPEECH BALLOON}", False)
        emoji, is_human = self._sender_info.get(message.sender, default)
        bubble = ChatBubble(message.sender, emoji, message.text, is_human=is_human)
        log = self.query_one("#log", VerticalScroll)
        log.mount(bubble)
        log.scroll_end(animate=False)

    async def _collect_replies(
        self, initial_message: ChatMessage
    ) -> AsyncGenerator[ChatMessage, None]:
        """Yield reply messages in BFS order with no UI side effects.

        Pure async generator: given an initial message and the registered
        participants, produces every reply that flows from it. The caller
        is responsible for display and for stamping fresh timestamps.
        """
        queue: list[ChatMessage] = [initial_message]
        while queue:
            message = queue.pop(0)
            for participant in self._participants:
                reply = await participant.on_message(message)
                if reply is not None:
                    # Stamp the timestamp here in the shell, not inside the bot
                    stamped = ChatMessage(
                        sender=reply.sender,
                        text=reply.text,
                        timestamp=datetime.now(tz=UTC),
                    )
                    queue.append(stamped)
                    yield stamped

    async def _dispatch(self, initial_message: ChatMessage) -> None:
        """Consume replies from _collect_replies and render them to the log."""
        async for reply in self._collect_replies(initial_message):
            self._append_to_log(reply)
