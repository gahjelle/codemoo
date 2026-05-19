"""Textual TUI application wiring together chat participants."""

import asyncio
import contextlib
import dataclasses
from collections.abc import AsyncGenerator, Awaitable, Callable, Sequence
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.css.query import NoMatches
from textual.events import Key
from textual.widgets import Label

from codemoo.chat.approval import ApprovalModal
from codemoo.chat.backend_status import BackendStatus
from codemoo.chat.bubble import ChatBubble
from codemoo.chat.context_status import ContextStatus
from codemoo.chat.demo_header import DemoHeader
from codemoo.chat.input import ChatInput
from codemoo.chat.slides import DemoContext, SlideScreen
from codemoo.chat.status import ThinkingStatus
from codemoo.config.schema import ResolvedBotConfig
from codemoo.core.bots.approval import ApprovalRequest, GuardDecision
from codemoo.core.bots.commentator_bot import CommentatorBot, ContextEvent
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.context_builder import build_context
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    UserMessageContent,
    next_turn_id,
)
from codemoo.core.message import ChatMessage
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.core.token_counter import estimate_tokens
from codemoo.core.tools.shell import _run_shell
from codemoo.llm.factory import BackendInfo


def _bind_context_management(app: "ChatApp") -> None:
    app.mount(ContextStatus(), after="BackendStatus")


_CAPABILITY_BINDERS: dict[str, Callable[["ChatApp"], None]] = {
    "context_management": _bind_context_management,
}


class ChatApp(App[str | None]):
    """Main TUI application that hosts the chat log and input widget."""

    CSS_PATH = Path(__file__).parent / "chat.tcss"

    def __init__(  # noqa: PLR0913
        self,
        human: HumanParticipant,
        participants: Sequence[ChatParticipant],
        error_bot: ErrorBot,
        commentator_bot: CommentatorBot | None = None,
        demo_context: DemoContext | None = None,
        backend_info: BackendInfo | None = None,
        resolved_bots: list[ResolvedBotConfig] | None = None,
    ) -> None:
        """Initialise with the human, bot participants, and error bot."""
        super().__init__()
        self._human = human
        self._participants = list(participants)
        self._error_bot = error_bot
        self._demo_context = demo_context
        self._backend_info = backend_info
        self._resolved_bots = resolved_bots or []

        # Build a lookup from sender name → (emoji, css_class)
        self._sender_info: dict[str, tuple[str, str]] = {
            p.name: (p.emoji, "bubble--bot") for p in participants
        }
        self._sender_info[human.name] = (human.emoji, "bubble--human")
        self._sender_info[error_bot.name] = (error_bot.emoji, "bubble--error")
        self._sender_info["Shell"] = (
            "\N{PERSONAL COMPUTER}",
            "bubble--shell bubble--verbatim",
        )
        self._active_capabilities: frozenset[str] = frozenset(
            cap for r in self._resolved_bots for cap in r.capabilities
        )
        self._commentator_bot = commentator_bot
        if commentator_bot is not None:
            self._sender_info |= commentator_bot.sender_info()
        for participant in participants:
            if hasattr(participant, "register_guard"):
                participant.register_guard(self._make_guard_ask_fn())  # ty: ignore[call-non-callable]
        # Authoritative context for the session, owned by the App
        self._chat_context: list[ContextItem] = []
        self._prompt_index = 0

    def compose(self) -> ComposeResult:
        """Yield the scrollable log, thinking status bar, input, and backend footer."""
        if self._demo_context is not None:
            bot = self._participants[0]
            prompt_count = len(self._demo_context.prompts)
            yield DemoHeader(bot, self._demo_context.position, prompt_count)
        yield VerticalScroll(id="log")
        yield ThinkingStatus()
        yield ChatInput(
            placeholder="Type a message... (Enter to send, Alt-N for newline)"
        )
        if self._backend_info is not None:
            yield BackendStatus(self._backend_info, self._resolved_bots)

    async def on_mount(self) -> None:
        """Push the slide overlay when entering demo mode and focus the input."""
        if self._commentator_bot is not None:
            self._commentator_bot.register(self._append_to_log)
        for cap in self._active_capabilities:
            if bind := _CAPABILITY_BINDERS.get(cap):
                bind(self)
        self.run_worker(self._run_startup())
        if self._demo_context is not None:
            self.push_screen(SlideScreen(self._demo_context))
        self.query_one(ChatInput).focus()

    async def _run_startup(self) -> None:
        for participant in self._participants:
            if hasattr(participant, "startup"):
                await participant.startup()  # ty: ignore[call-non-callable]

    def on_chat_input_submitted(self, event: ChatInput.Submitted) -> None:
        """Handle Enter: shell-mode for `!` prefix, bot dispatch otherwise."""
        text = event.value
        self._append_to_log(ChatMessage(sender=self._human.name, text=text))
        if text.startswith("!"):
            self.run_worker(self._handle_shell_input(text[1:].strip()), exclusive=False)
            return
        self._chat_context = [
            *self._chat_context,
            ContextItem(
                content=UserMessageContent(text),
                turn_id=next_turn_id(self._chat_context),
            ),
        ]
        # Dispatch in a worker so participant coroutines run without blocking the UI
        self.run_worker(
            self._dispatch(ChatMessage(sender=self._human.name, text=text)),
            exclusive=False,
        )

    async def _handle_shell_input(self, command: str) -> None:
        """Run a user-typed shell command verbatim; output bypasses context."""
        output = _run_shell(command)
        self._append_to_log(ChatMessage(sender="Shell", text=output))
        self.copy_to_clipboard(output)

    def _append_to_log(self, message: ChatMessage) -> None:
        default = ("\N{SPEECH BALLOON}", "bubble--commentator")
        emoji, css_class = self._sender_info.get(message.sender, default)
        bubble = ChatBubble(
            message.sender,
            emoji,
            message.text,
            thinking_time=message.thinking_time,
            css_class=css_class,
        )
        log = self.query_one("#log", VerticalScroll)
        log.mount(bubble)
        log.scroll_end(animate=False)

    def _reply_from_items(
        self, participant: ChatParticipant, items: list[ContextItem]
    ) -> ChatMessage | None:
        if items and isinstance(items[-1].content, AssistantMessageContent):
            return ChatMessage(sender=participant.name, text=items[-1].content.text)
        return None

    async def _collect_replies(  # noqa: C901
        self,
        initial_message: ChatMessage,
        status: ThinkingStatus | None = None,
    ) -> AsyncGenerator[ChatMessage, None]:
        """Yield reply messages in BFS order.

        status is optional so that tests can call this generator directly without
        a running Textual app. When provided, it is updated before and after each
        participant call. Exceptions are surfaced as ErrorBot messages that are
        yielded to the log but not re-queued for dispatch.
        """
        queue: list[ChatMessage] = [initial_message]
        while queue:
            message = queue.pop(0)
            for participant in self._participants:
                if message.sender == participant.name:
                    continue
                if status:
                    status.set_bot(participant.emoji, participant.name)
                reply = None
                try:
                    if hasattr(participant, "compact"):
                        self._chat_context = await participant.compact(
                            self._chat_context
                        )  # ty: ignore[call-non-callable]
                    # Invariant: self._chat_context[-1] is the triggering message
                    new_items = await participant.on_message(self._chat_context)
                    self._chat_context = [*self._chat_context, *new_items]
                    reply = self._reply_from_items(participant, new_items)
                    # Capture thinking time for successful replies
                    thinking_time = status.clear() if status else None
                    if thinking_time is not None and reply is not None:
                        reply = dataclasses.replace(reply, thinking_time=thinking_time)
                except Exception as exc:  # noqa: BLE001
                    # Clear status but don't capture time for failed bots
                    if status:
                        status.clear()
                    yield await self._error_bot.format_error(participant, exc)
                    continue
                finally:
                    # Ensure status is cleared even if no exception but reply is None
                    if status and reply is None:
                        status.clear()
                if reply is not None:
                    queue.append(reply)
                    yield reply

    async def _dispatch(self, initial_message: ChatMessage) -> None:
        """Consume replies from _collect_replies and render them to the log."""
        status = self.query_one(ThinkingStatus)
        async for reply in self._collect_replies(initial_message, status):
            self._append_to_log(reply)
        with contextlib.suppress(NoMatches):
            token_count = estimate_tokens(build_context(self._chat_context))
            self.query_one(ContextStatus).update_context(
                len(self._chat_context), token_count
            )

    def _make_guard_ask_fn(
        self,
    ) -> Callable[[ApprovalRequest], Awaitable[GuardDecision]]:
        """Return an async callable that shows ApprovalModal and awaits the result."""

        async def ask_fn(request: ApprovalRequest) -> GuardDecision:
            loop = asyncio.get_running_loop()
            future: asyncio.Future[GuardDecision] = loop.create_future()
            self.push_screen(ApprovalModal(request), future.set_result)
            return await future

        return ask_fn

    def on_key(self, event: Key) -> None:
        """Handle demo-mode keyboard shortcuts (Ctrl-N, Ctrl-E, Ctrl-S, Ctrl-R)."""
        if self._demo_context is None:
            return
        if event.key == "ctrl+n":
            self.exit("next")
        elif event.key == "ctrl+e":
            self._insert_next_prompt()
        elif event.key == "ctrl+s":
            self._reopen_slide()
        elif event.key == "ctrl+r":
            self._restart_bot()

    def _reopen_slide(self) -> None:
        if self._demo_context is None:
            return
        if any(isinstance(s, SlideScreen) for s in self.screen_stack):
            return
        self.push_screen(SlideScreen(self._demo_context))

    def _restart_bot(self) -> None:
        if self._demo_context is None:
            return
        log = self.query_one("#log", VerticalScroll)
        log.mount(
            Label(
                "\N{ANTICLOCKWISE OPEN CIRCLE ARROW} Restarted",
                classes="restart-divider",
            )
        )
        log.scroll_end(animate=False)
        if self._commentator_bot is not None:
            bot = self._participants[0]
            message_texts = [
                item.content.text[:300]
                for item in self._chat_context
                if isinstance(
                    item.content, (UserMessageContent, AssistantMessageContent)
                )
            ]
            preview = "\n".join(message_texts[-2:])
            self.run_worker(
                self._commentator_bot.comment(
                    ContextEvent(
                        kind="restart",
                        bot_name=bot.name,
                        items_affected=len(self._chat_context),
                        preview=preview,
                    )
                )
            )
        self._chat_context = []
        self._prompt_index = 0
        prompts = self._demo_context.prompts
        self.query_one(DemoHeader).update_prompt_state(len(prompts))
        self.run_worker(self._run_startup())

    def _insert_next_prompt(self) -> None:
        if self._demo_context is None:
            return
        prompts = self._demo_context.prompts
        if self._prompt_index >= len(prompts):
            return
        self.query_one(ChatInput).load_text(prompts[self._prompt_index])
        self._prompt_index += 1
        remaining = len(prompts) - self._prompt_index
        self.query_one(DemoHeader).update_prompt_state(remaining)
