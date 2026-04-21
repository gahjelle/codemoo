"""Tests for ChatApp._collect_replies.

Exercises the pure dispatch logic without requiring a running Textual application.
"""

from datetime import UTC, datetime

import pytest

from codemoo.chat.app import ChatApp
from codemoo.core.message import ChatMessage
from codemoo.core.participant import ChatParticipant, HumanParticipant


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

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
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

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        history: list[ChatMessage],  # noqa: ARG002
    ) -> ChatMessage | None:
        return None


class _HistoryCapturingParticipant:
    """Participant that records the history it receives on each call."""

    def __init__(self) -> None:
        self.received_histories: list[list[ChatMessage]] = []

    @property
    def name(self) -> str:
        return "HistoryCapture"

    @property
    def emoji(self) -> str:
        return "\N{CLIPBOARD}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(
        self,
        message: ChatMessage,  # noqa: ARG002
        history: list[ChatMessage],
    ) -> ChatMessage | None:
        self.received_histories.append(list(history))
        return None


_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _make_app(participants: list[ChatParticipant]) -> ChatApp:
    return ChatApp(participants=participants)


@pytest.mark.asyncio
async def test_collect_replies_yields_echo_reply() -> None:
    app = _make_app([HumanParticipant(), _EchoParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial, [])]
    assert len(replies) == 1
    assert replies[0].sender == "Echo"
    assert replies[0].text == "hi"


@pytest.mark.asyncio
async def test_collect_replies_yields_nothing_for_silent_bot() -> None:
    app = _make_app([HumanParticipant(), _SilentParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial, [])]
    assert replies == []


@pytest.mark.asyncio
async def test_collect_replies_does_not_loop_on_echo() -> None:
    # The echo bot filters its own messages, so the chain must terminate.
    app = _make_app([HumanParticipant(), _EchoParticipant()])
    initial = ChatMessage(sender="You", text="ping", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial, [])]
    # Exactly one reply: the echo. The echo bot's reply is not echoed again.
    assert len(replies) == 1


@pytest.mark.asyncio
async def test_history_passed_to_participants_excludes_current_message() -> None:
    capture = _HistoryCapturingParticipant()
    app = _make_app([HumanParticipant(), capture])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    [_ async for _ in app._collect_replies(initial, [])]
    assert capture.received_histories[0] == []


@pytest.mark.asyncio
async def test_history_passed_includes_prior_messages() -> None:
    prior = ChatMessage(sender="You", text="earlier", timestamp=_TS)
    capture = _HistoryCapturingParticipant()
    app = _make_app([HumanParticipant(), capture])
    initial = ChatMessage(sender="You", text="now", timestamp=_TS)

    [_ async for _ in app._collect_replies(initial, [prior])]
    assert capture.received_histories[0] == [prior]
