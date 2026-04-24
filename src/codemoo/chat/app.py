"""Textual TUI application wiring together chat participants."""

from collections.abc import AsyncGenerator, Sequence
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.events import Key
from textual.widgets import Input

from codemoo.chat.backend_status import BackendStatus
from codemoo.chat.bubble import ChatBubble
from codemoo.chat.demo_header import DemoHeader
from codemoo.chat.slides import DemoContext, SlideScreen
from codemoo.chat.status import ThinkingStatus
from codemoo.core.bots.commentator_bot import CommentatorBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.message import ChatMessage
from codemoo.core.participant import ChatParticipant
from codemoo.llm.factory import BackendInfo


class ChatApp(App[str | None]):
    """Main TUI application that hosts the chat log and input widget."""

    CSS_PATH = Path(__file__).parent / "chat.tcss"

    def __init__(
        self,
        participants: Sequence[ChatParticipant],
        error_bot: ErrorBot,
        commentator_bot: CommentatorBot | None = None,
        demo_context: DemoContext | None = None,
        backend_info: BackendInfo | None = None,
    ) -> None:
        """Initialise with an ordered list of chat participants and the error bot."""
        super().__init__()
        self._participants = list(participants)
        self._error_bot = error_bot
        self._demo_context = demo_context
        self._backend_info = backend_info

        # Build a lookup from sender name → (emoji, is_human, css_class)
        def _bubble_class(p: ChatParticipant) -> str:
            return "bubble--human" if p.is_human else "bubble--bot"

        self._sender_info: dict[str, tuple[str, bool, str]] = {
            p.name: (p.emoji, p.is_human, _bubble_class(p)) for p in participants
        }
        self._sender_info[error_bot.name] = (error_bot.emoji, False, "bubble--error")
        if commentator_bot is not None:
            self._sender_info |= commentator_bot.sender_info()
            commentator_bot.register(self._append_to_log)
        # Keep a reference to the human participant for outgoing message construction
        self._human = next(p for p in participants if p.is_human)
        # Authoritative ordered history of all messages posted in this session
        self._history: list[ChatMessage] = []

    def compose(self) -> ComposeResult:
        """Yield the scrollable log, thinking status bar, input, and backend footer."""
        if self._demo_context is not None:
            bot = next(p for p in self._participants if not p.is_human)
            yield DemoHeader(bot, self._demo_context.position)
        yield VerticalScroll(id="log")
        yield ThinkingStatus()
        yield Input(placeholder="Type a message and press Enter...")
        if self._backend_info is not None:
            yield BackendStatus(self._backend_info)

    def on_mount(self) -> None:
        """Push the slide overlay when entering demo mode."""
        if self._demo_context is not None:
            self.push_screen(SlideScreen(self._demo_context))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter in the input box: create a message and dispatch it."""
        text = event.value.strip()
        # Empty input produces no message per spec
        if not text:
            return
        self.query_one(Input).clear()
        message = ChatMessage(sender=self._human.name, text=text)
        self._append_to_log(message)
        # Snapshot before appending: history excludes the current message
        prior_history = list(self._history)
        self._history.append(message)
        # Dispatch in a worker so participant coroutines run without blocking the UI
        self.run_worker(self._dispatch(message, prior_history), exclusive=False)

    def _append_to_log(self, message: ChatMessage) -> None:
        default = ("\N{SPEECH BALLOON}", False, "bubble--commentator")
        emoji, is_human, css_class = self._sender_info.get(message.sender, default)
        bubble = ChatBubble(
            message.sender, emoji, message.text, is_human=is_human, css_class=css_class
        )
        log = self.query_one("#log", VerticalScroll)
        log.mount(bubble)
        log.scroll_end(animate=False)

    async def _collect_replies(
        self,
        initial_message: ChatMessage,
        history: list[ChatMessage],
        status: ThinkingStatus | None = None,
    ) -> AsyncGenerator[ChatMessage, None]:
        """Yield reply messages in BFS order.

        status is optional so that tests can call this generator directly without
        a running Textual app. When provided, it is updated before and after each
        participant call. Exceptions are surfaced as ErrorBot messages that are
        yielded to the log but not re-queued for dispatch.
        """
        running_history = list(history)
        queue: list[ChatMessage] = [initial_message]
        while queue:
            message = queue.pop(0)
            for participant in self._participants:
                if message.sender == participant.name:
                    continue
                if status and not participant.is_human:
                    status.set_bot(participant.emoji, participant.name)
                try:
                    reply = await participant.on_message(message, running_history)
                except Exception as exc:  # noqa: BLE001
                    yield await self._error_bot.format_error(participant, exc)
                    continue
                finally:
                    if status:
                        status.clear()
                if reply is not None:
                    queue.append(reply)
                    yield reply
            running_history.append(message)

    async def _dispatch(
        self, initial_message: ChatMessage, history: list[ChatMessage]
    ) -> None:
        """Consume replies from _collect_replies and render them to the log."""
        status = self.query_one(ThinkingStatus)
        replies: list[ChatMessage] = []
        async for reply in self._collect_replies(initial_message, history, status):
            self._append_to_log(reply)
            replies.append(reply)
        self._history.extend(replies)

    def on_key(self, event: Key) -> None:
        """Advance to the next bot when Ctrl-N is pressed in demo mode."""
        if event.key == "ctrl+n" and self._demo_context is not None:
            self.exit("next")
