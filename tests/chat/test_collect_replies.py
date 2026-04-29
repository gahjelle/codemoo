"""Tests for ChatApp._collect_replies.

Exercises the pure dispatch logic without requiring a running Textual application.
"""

from datetime import UTC, datetime

import pytest

from codemoo.chat.app import ChatApp
from codemoo.core.bots.error_bot import ErrorBot
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

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],
    ) -> ChatMessage | None:
        return ChatMessage(sender=self.name, text=message.text)


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
        message: ChatMessage,
        history: list[ChatMessage],
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
        message: ChatMessage,
        history: list[ChatMessage],
    ) -> ChatMessage | None:
        self.received_histories.append(list(history))
        return None


class _MessageCapturingParticipant:
    """Participant that records every message it receives."""

    def __init__(self, name: str) -> None:
        self._name = name
        self.received_messages: list[ChatMessage] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def emoji(self) -> str:
        return "\N{MEMO}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],
    ) -> ChatMessage | None:
        self.received_messages.append(message)
        return None


_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _make_app(participants: list[ChatParticipant]) -> ChatApp:
    return ChatApp(
        participants=participants,
        error_bot=ErrorBot(llm=_MockBackend()),
    )


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
    # The shell skips the sender, so the echo bot's reply is never dispatched back.
    app = _make_app([HumanParticipant(), _EchoParticipant()])
    initial = ChatMessage(sender="You", text="ping", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial, [])]
    # Exactly one reply: the echo. The echo bot's reply is not echoed again.
    assert len(replies) == 1


@pytest.mark.asyncio
async def test_sender_is_not_called_with_own_message() -> None:
    # The shell must skip the sender — the bot should never receive its own message.
    capture = _MessageCapturingParticipant("Bot")
    app = _make_app([HumanParticipant(), capture])
    own_message = ChatMessage(sender="Bot", text="I said this", timestamp=_TS)

    [_ async for _ in app._collect_replies(own_message, [])]
    assert all(m.sender != "Bot" for m in capture.received_messages)


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


class _FailingParticipant:
    """Participant whose on_message always raises."""

    @property
    def name(self) -> str:
        return "Failer"

    @property
    def emoji(self) -> str:
        return "\N{COLLISION SYMBOL}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(
        self,
        message: ChatMessage,
        history: list[ChatMessage],
    ) -> ChatMessage | None:
        msg = "simulated LLM failure"
        raise RuntimeError(msg)


@pytest.mark.asyncio
async def test_exception_yields_error_bubble_not_crash() -> None:
    app = _make_app([HumanParticipant(), _FailingParticipant()])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    replies = [r async for r in app._collect_replies(initial, [])]
    assert len(replies) == 1
    assert replies[0].sender == app._error_bot.name


@pytest.mark.asyncio
async def test_exception_does_not_block_remaining_participants() -> None:
    capture = _MessageCapturingParticipant("Capture")
    app = _make_app([HumanParticipant(), _FailingParticipant(), capture])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    [_ async for _ in app._collect_replies(initial, [])]
    # The capture participant must still have received the message
    assert any(m.text == "hi" for m in capture.received_messages)


@pytest.mark.asyncio
async def test_error_message_is_not_dispatched_to_other_bots() -> None:
    # Error messages must not re-enter the BFS queue — no bot should respond to them.
    capture = _MessageCapturingParticipant("Capture")
    app = _make_app([HumanParticipant(), _FailingParticipant(), capture])
    initial = ChatMessage(sender="You", text="hi", timestamp=_TS)

    [_ async for _ in app._collect_replies(initial, [])]
    # The capture participant must not have received the error bot's message
    error_name = app._error_bot.name
    assert all(m.sender != error_name for m in capture.received_messages)
