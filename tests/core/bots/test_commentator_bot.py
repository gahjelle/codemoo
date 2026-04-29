"""Tests for CommentatorBot, ToolCallEvent, and persona fallback."""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from codemoo.chat.app import ChatApp
from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.commentator_bot import (
    _PERSONAS,
    _STREIK_NAME,
    CommentatorBot,
    ToolCallEvent,
)
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot
from codemoo.core.message import ChatMessage
from codemoo.core.participant import HumanParticipant
from codemoo.core.tools import run_shell

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
_PERSONA_NAMES = {p.name for p in _PERSONAS}


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


# ---------------------------------------------------------------------------
# 6.1 ToolCallEvent
# ---------------------------------------------------------------------------


def test_tool_call_event_fields() -> None:
    event = ToolCallEvent(
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "echo hi"},
    )
    assert event.bot_name == "Loom"
    assert event.tool_name == "run_shell"
    assert event.arguments == {"command": "echo hi"}


# ---------------------------------------------------------------------------
# 6.2 CommentatorBot happy path
# ---------------------------------------------------------------------------


class _MockBackend:
    def __init__(self, response: str = "commentary text") -> None:
        self._response = response
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.calls.append(messages)
        return self._response


@pytest.mark.asyncio
async def test_comment_happy_path_posts_message_with_persona_sender() -> None:
    backend = _MockBackend(response="Oh wow, a shell command!")
    bot = CommentatorBot(llm=backend)
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolCallEvent(
        bot_name="Loom", tool_name="run_shell", arguments={"command": "ls"}
    )
    await bot.comment(event)

    assert len(received) == 1
    assert received[0].sender in _PERSONA_NAMES
    assert "Oh wow, a shell command!" in received[0].text
    assert "run_shell" in received[0].text
    assert "[dim]" in received[0].text


@pytest.mark.asyncio
async def test_comment_passes_event_info_in_prompt() -> None:
    backend = _MockBackend()
    bot = CommentatorBot(llm=backend)
    bot.register(lambda _: None)

    event = ToolCallEvent(
        bot_name="Ash", tool_name="read_file", arguments={"path": "README.md"}
    )
    await bot.comment(event)

    assert backend.calls
    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "Ash" in user_msg.content
    assert "read_file" in user_msg.content


# ---------------------------------------------------------------------------
# 6.3 Streik fallback
# ---------------------------------------------------------------------------


class _FailingBackend:
    async def complete(self, messages: list[Message]) -> str:
        msg = "LLM exploded"
        raise RuntimeError(msg)


@pytest.mark.asyncio
async def test_streik_fallback_on_llm_error() -> None:
    bot = CommentatorBot(llm=_FailingBackend())
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolCallEvent(
        bot_name="Loom", tool_name="run_shell", arguments={"command": "ls"}
    )
    await bot.comment(event)  # must not raise

    assert len(received) == 1
    assert received[0].sender == _STREIK_NAME


@pytest.mark.asyncio
async def test_streik_fallback_text_contains_tool_name_and_bot_name() -> None:
    bot = CommentatorBot(llm=_FailingBackend())
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolCallEvent(
        bot_name="Ash", tool_name="read_file", arguments={"path": "SCRIPT.md"}
    )
    await bot.comment(event)

    text = received[0].text
    assert "Ash" in text
    assert "read_file" in text
    assert "SCRIPT.md" in text


# ---------------------------------------------------------------------------
# 6.4 SingleTurnToolBot calls commentator before tool fn
# ---------------------------------------------------------------------------

_TOOL_USE = ToolUse(
    name="run_shell",
    arguments={"command": "echo hi"},
    call_id="c1",
    assistant_message=Message(
        role="assistant",
        content="",
        tool_calls_json=(
            '[{"id":"c1","type":"function","function":'
            '{"name":"run_shell","arguments":"{\\"command\\":\\"echo hi\\"}"}}]'
        ),
    ),
)


class _SingleStepBackend:
    def __init__(self, step: TextResponse | ToolUse) -> None:
        self._step = step

    async def complete(self, messages: list[Message]) -> str:
        return "done"

    async def complete_step(
        self, messages: list[Message], tools: object
    ) -> TextResponse | ToolUse:
        return self._step


@pytest.mark.asyncio
async def test_single_turn_tool_bot_calls_commentator_before_tool() -> None:
    call_order: list[str] = []

    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(
        side_effect=lambda _: call_order.append("comment")
    )

    def _tracked_fn(**kwargs: object) -> str:
        call_order.append("tool")
        return "output"

    bot = SingleTurnToolBot(
        name="Ash",
        emoji="🐚",
        llm=_SingleStepBackend(_TOOL_USE),
        tools=[run_shell],
        instructions="",
        commentator=mock_commentator,
    )

    with patch.object(run_shell, "fn", _tracked_fn):
        await bot.on_message(_msg("You", "run it"), [])

    assert call_order == ["comment", "tool"]


# ---------------------------------------------------------------------------
# 6.5 AgentBot calls commentator on each tool call in a multi-step loop
# ---------------------------------------------------------------------------


class _MultiStepBackend:
    def __init__(self, steps: list[TextResponse | ToolUse]) -> None:
        self._steps = list(steps)

    async def complete(self, messages: list[Message]) -> str:
        pytest.fail("AgentBot should not call complete()")

    async def complete_step(
        self, messages: list[Message], tools: object
    ) -> TextResponse | ToolUse:
        return self._steps.pop(0)


def _tool_use(call_id: str) -> ToolUse:
    args = '{\\"command\\":\\"echo hi\\"}'
    return ToolUse(
        name="run_shell",
        arguments={"command": "echo hi"},
        call_id=call_id,
        assistant_message=Message(
            role="assistant",
            content="",
            tool_calls_json=(
                f'[{{"id":"{call_id}","type":"function","function":'
                f'{{"name":"run_shell","arguments":"{args}"}}}}'
                f"]"
            ),
        ),
    )


@pytest.mark.asyncio
async def test_agent_bot_calls_commentator_per_tool_step() -> None:
    comment_events: list[ToolCallEvent] = []
    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(side_effect=comment_events.append)

    backend = _MultiStepBackend(
        [_tool_use("c1"), _tool_use("c2"), TextResponse(text="all done")]
    )
    bot = AgentBot(
        name="Loom",
        emoji="🌀",
        llm=backend,
        tools=[run_shell],
        instructions="You are a helpful assistant.",
        commentator=mock_commentator,
    )

    await bot.on_message(_msg("You", "do two things"), [])

    assert len(comment_events) == 2
    assert all(isinstance(e, ToolCallEvent) for e in comment_events)


# ---------------------------------------------------------------------------
# 6.6 ChatApp._append_to_log fallback for unknown sender
# ---------------------------------------------------------------------------


class _NullBackend:
    async def complete(self, messages: object) -> str:
        return ""


def _make_app() -> ChatApp:
    return ChatApp(
        participants=[HumanParticipant()],
        error_bot=ErrorBot(llm=_NullBackend()),
    )


def test_unknown_sender_resolved_to_commentator_class() -> None:
    app = _make_app()
    default = ("\N{SPEECH BALLOON}", False, "bubble--commentator")
    _, _, css_class = app._sender_info.get("UnknownPersona", default)
    assert css_class == "bubble--commentator"


def test_known_senders_are_not_affected() -> None:
    human = HumanParticipant()
    app = _make_app()
    _, _, css_class = app._sender_info[human.name]
    assert css_class == "bubble--human"


# ---------------------------------------------------------------------------
# sender_info() and emoji registration
# ---------------------------------------------------------------------------


def test_sender_info_contains_all_personas() -> None:
    bot = CommentatorBot(llm=_NullBackend())
    info = bot.sender_info()
    for persona in _PERSONAS:
        assert persona.name in info
        emoji, _, css = info[persona.name]
        assert emoji == persona.emoji
        assert css == "bubble--commentator"


def test_sender_info_contains_streik() -> None:
    bot = CommentatorBot(llm=_NullBackend())
    info = bot.sender_info()
    assert _STREIK_NAME in info
    _, _, css = info[_STREIK_NAME]
    assert css == "bubble--commentator"


def test_chat_app_registers_persona_emojis_when_commentator_provided() -> None:
    bot = CommentatorBot(llm=_NullBackend())
    app = ChatApp(
        participants=[HumanParticipant()],
        error_bot=ErrorBot(llm=_NullBackend()),
        commentator_bot=bot,
    )
    for persona in _PERSONAS:
        assert persona.name in app._sender_info
        emoji, _, _ = app._sender_info[persona.name]
        assert emoji == persona.emoji


@pytest.mark.asyncio
async def test_display_header_truncates_long_values_with_ellipsis() -> None:
    backend = _MockBackend(response="Nice!")
    bot = CommentatorBot(llm=backend)
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolCallEvent(
        bot_name="Loom",
        tool_name="write_file",
        arguments={"path": "f.py", "content": "x" * 200},
    )
    await bot.comment(event)

    assert len(received) == 1
    text = received[0].text
    assert "[dim]" in text
    assert "\N{HORIZONTAL ELLIPSIS}" in text


def test_streik_fallback_has_no_dim_prefix() -> None:
    """Streik posts just the call sig with no [dim] markup."""

    async def _run() -> ChatMessage:
        bot = CommentatorBot(llm=_FailingBackend())
        received: list[ChatMessage] = []
        bot.register(received.append)
        event = ToolCallEvent(
            bot_name="Ash", tool_name="read_file", arguments={"path": "x.md"}
        )
        await bot.comment(event)
        return received[0]

    msg = asyncio.run(_run())
    assert "[dim]" not in msg.text
