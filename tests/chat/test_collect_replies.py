"""Tests for ChatApp._collect_replies.

Exercises the pure dispatch logic without requiring a running Textual application.
"""

from datetime import UTC, datetime

import pytest

from codemoo.chat.app import ChatApp
from codemoo.config.schema import ResolvedBotConfig
from codemoo.core.context_items import ContextItem, UserMessageContent
from codemoo.core.error import ErrorBot
from codemoo.core.message import ChatMessage
from codemoo.core.participant import ChatParticipant, HumanParticipant


class _MockBackend:
    def __init__(self, response: str = "error description") -> None:
        self.response = response

    async def complete(self, messages: object) -> str:
        return self.response


class _EchoParticipant:
    """Minimal bot that echoes every message it receives."""

    @property
    def name(self) -> str:
        return "Echo"

    @property
    def emoji(self) -> str:
        return "\N{ROBOT FACE}"

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        from codemoo.core.context_items import AssistantMessageContent, next_turn_id

        return [
            ContextItem(
                content=AssistantMessageContent(context[-1].content.text),  # ty: ignore[unresolved-attribute]
                turn_id=next_turn_id(context),
            )
        ]


class _SilentParticipant:
    """Participant that never replies."""

    @property
    def name(self) -> str:
        return "Silent"

    @property
    def emoji(self) -> str:
        return "\N{ZIPPER-MOUTH FACE}"

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        return []


class _ContextCapturingParticipant:
    """Participant that records the context it receives on each call."""

    def __init__(self) -> None:
        self.received_contexts: list[list[ContextItem]] = []

    @property
    def name(self) -> str:
        return "ContextCapture"

    @property
    def emoji(self) -> str:
        return "\N{CLIPBOARD}"

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        self.received_contexts.append(list(context))
        return []


class _TextCapturingParticipant:
    """Participant that records the triggering text from each call."""

    def __init__(self, name: str) -> None:
        self._name = name
        self.received_texts: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def emoji(self) -> str:
        return "\N{MEMO}"

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        self.received_texts.append(context[-1].content.text)  # ty: ignore[unresolved-attribute]
        return []


_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
_HUMAN = HumanParticipant()


def _make_app(participants: list[ChatParticipant]) -> ChatApp:
    return ChatApp(
        human=_HUMAN,
        participants=participants,
        error_bot=ErrorBot(llm=_MockBackend()),
    )


def _seed_context(app: ChatApp, text: str) -> None:
    """Establish the on_message invariant: add triggering item before dispatch."""
    app._chat_context = [
        *app._chat_context,
        ContextItem(content=UserMessageContent(text)),
    ]


@pytest.mark.asyncio
async def test_collect_replies_yields_echo_reply() -> None:
    app = _make_app([_EchoParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)
    _seed_context(app, initial.text)

    replies = [r async for r in app._collect_replies(initial)]
    assert len(replies) == 1
    assert replies[0].sender == "Echo"
    assert replies[0].text == "hi"


@pytest.mark.asyncio
async def test_collect_replies_yields_nothing_for_silent_bot() -> None:
    app = _make_app([_SilentParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)
    _seed_context(app, initial.text)

    replies = [r async for r in app._collect_replies(initial)]
    assert replies == []


@pytest.mark.asyncio
async def test_collect_replies_does_not_loop_on_echo() -> None:
    # The shell skips the sender, so the echo bot's reply is never dispatched back.
    app = _make_app([_EchoParticipant()])
    initial = ChatMessage(sender="You", text="ping", timestamp=_TS)
    _seed_context(app, initial.text)

    replies = [r async for r in app._collect_replies(initial)]
    # Exactly one reply: the echo. The echo bot's reply is not echoed again.
    assert len(replies) == 1


@pytest.mark.asyncio
async def test_sender_is_not_called_with_own_message() -> None:
    # The shell must skip the sender — the bot should never receive its own message.
    capture = _TextCapturingParticipant("Bot")
    app = _make_app([capture])
    own_message = ChatMessage(sender="Bot", text="I said this", timestamp=_TS)
    _seed_context(app, own_message.text)

    [_ async for _ in app._collect_replies(own_message)]
    # "Bot" sent the message; it must not have been dispatched back to itself
    assert len(capture.received_texts) == 0


@pytest.mark.asyncio
async def test_context_passed_to_participants_reflects_app_context() -> None:
    capture = _ContextCapturingParticipant()
    app = _make_app([capture])
    prior_item = ContextItem(content=UserMessageContent("earlier"))
    app._chat_context = [prior_item]
    initial = ChatMessage(sender="You", text="now", timestamp=_TS)
    _seed_context(app, initial.text)

    [_ async for _ in app._collect_replies(initial)]
    # prior_item and triggering item must both be in the context received
    assert prior_item in capture.received_contexts[0]
    assert capture.received_contexts[0][-1].content == UserMessageContent("now")


class _FailingParticipant:
    """Participant whose on_message always raises."""

    @property
    def name(self) -> str:
        return "Failer"

    @property
    def emoji(self) -> str:
        return "\N{COLLISION SYMBOL}"

    async def on_message(self, context: list[ContextItem]) -> list[ContextItem]:
        msg = "simulated LLM failure"
        raise RuntimeError(msg)


@pytest.mark.asyncio
async def test_exception_yields_error_bubble_not_crash() -> None:
    app = _make_app([_FailingParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)
    _seed_context(app, initial.text)

    replies = [r async for r in app._collect_replies(initial)]
    assert len(replies) == 1
    assert replies[0].sender == app._error_bot.name


@pytest.mark.asyncio
async def test_exception_does_not_block_remaining_participants() -> None:
    capture = _TextCapturingParticipant("Capture")
    app = _make_app([_FailingParticipant(), capture])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)
    _seed_context(app, initial.text)

    [_ async for _ in app._collect_replies(initial)]
    # The capture participant must still have received the triggering message
    assert any(t == "hi" for t in capture.received_texts)


@pytest.mark.asyncio
async def test_error_message_is_not_dispatched_to_other_bots() -> None:
    # Error messages must not re-enter the BFS queue — no bot should respond to them.
    capture = _TextCapturingParticipant("Capture")
    app = _make_app([_FailingParticipant(), capture])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)
    _seed_context(app, initial.text)

    [_ async for _ in app._collect_replies(initial)]
    # Capture receives "hi" from the initial dispatch but not any error bot message
    assert len(capture.received_texts) == 1


# ---------------------------------------------------------------------------
# ChatApp._active_capabilities
# ---------------------------------------------------------------------------


def _make_resolved(capabilities: list[str]) -> ResolvedBotConfig:
    return ResolvedBotConfig(
        bot_type="EchoBot",
        name="Echo",
        emoji="\N{ROBOT FACE}",
        variant="default",
        sources=[],
        description="A bot.",
        tools=[],
        prompts=[],
        instructions="",
        context_source=None,
        capabilities=capabilities,
    )


def test_active_capabilities_is_union_across_resolved_bots() -> None:
    r1 = _make_resolved(["context_management"])
    r2 = _make_resolved([])
    app = ChatApp(
        human=_HUMAN,
        participants=[],
        error_bot=ErrorBot(llm=_MockBackend()),
        resolved_bots=[r1, r2],
    )
    assert app._active_capabilities == frozenset({"context_management"})


def test_active_capabilities_empty_when_no_capabilities_declared() -> None:
    app = ChatApp(
        human=_HUMAN,
        participants=[],
        error_bot=ErrorBot(llm=_MockBackend()),
        resolved_bots=[_make_resolved([])],
    )
    assert app._active_capabilities == frozenset()
