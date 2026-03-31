"""Tests for ChatApp._collect_replies.

Exercises the pure dispatch logic without requiring a running Textual application.
"""

from datetime import UTC, datetime

import pytest

from gaia.chat.app import ChatApp
from gaia.core.message import ChatMessage
from gaia.core.participant import ChatParticipant, HumanParticipant


class _EchoParticipant:
    """Minimal bot that echoes any message not from itself."""

    @property
    def name(self) -> str:
        return "Echo"

    @property
    def emoji(self) -> str:
        return "\N{ROBOT FACE}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:
        if message.sender == self.name:
            return None
        return ChatMessage(
            sender=self.name, text=message.text, timestamp=message.timestamp
        )


class _SilentParticipant:
    """Participant that never replies."""

    @property
    def name(self) -> str:
        return "Silent"

    @property
    def emoji(self) -> str:
        return "\N{ZIPPER-MOUTH FACE}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(self, message: ChatMessage) -> ChatMessage | None:  # noqa: ARG002
        return None


_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _make_app(participants: list[ChatParticipant]) -> ChatApp:
    return ChatApp(participants=participants)


@pytest.mark.asyncio
async def test_collect_replies_yields_echo_reply() -> None:
    app = _make_app([HumanParticipant(), _EchoParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial)]  # noqa: SLF001

    assert len(replies) == 1
    assert replies[0].sender == "Echo"
    assert replies[0].text == "hi"


@pytest.mark.asyncio
async def test_collect_replies_yields_nothing_for_silent_bot() -> None:
    app = _make_app([HumanParticipant(), _SilentParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial)]  # noqa: SLF001

    assert replies == []


@pytest.mark.asyncio
async def test_collect_replies_does_not_loop_on_echo() -> None:
    # The echo bot filters its own messages, so the chain must terminate.
    app = _make_app([HumanParticipant(), _EchoParticipant()])
    initial = ChatMessage(sender="You", text="ping", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial)]  # noqa: SLF001

    # Exactly one reply: the echo. The echo bot's reply is not echoed again.
    assert len(replies) == 1
