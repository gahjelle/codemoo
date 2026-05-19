"""Tests for CommentatorBot, ToolEvent, LoadEvent, and persona fallback."""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from codemoo.chat.app import ChatApp
from codemoo.core.backend import Message, ToolUse
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.bots.commentator_bot import (
    _STREIK_NAME,
    CommentatorBot,
    ContextEvent,
    LoadEvent,
    Persona,
    ToolEvent,
)
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.bots.single_turn_tool_bot import SingleTurnToolBot
from codemoo.core.message import ChatMessage
from codemoo.core.participant import HumanParticipant
from codemoo.core.tools.shell import run_shell
from tests.core.bots.conftest import user_ctx

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

_TEST_PERSONAS = [
    Persona(name="TestA", emoji="🎉", instructions="You are TestA."),
    Persona(name="TestB", emoji="📋", instructions="You are TestB."),
]
_TEST_PERSONA_NAMES = {p.name for p in _TEST_PERSONAS}

_TEST_TEMPLATES = {
    "call": "{bot_name} is calling '{tool_name}' with {sig}. Comment briefly.",
    "blocked": "{bot_name} was blocked calling '{tool_name}': {detail}. React.",
    "error": "{bot_name} got an error from '{tool_name}': {detail}. React.",
    "context": "{bot_name} loaded context from {source_desc} ({content_len} chars): {preview}",
    "memory": "{bot_name} loaded memory from {path} ({content_len} chars): {preview}",
    "restart": "{bot_name} restarted, dropping {items_affected} items. Last: {preview}. Lament.",
    "compact": "{bot_name} compacted {items_affected} items. Summary: {preview}. Celebrate.",
}


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


# ---------------------------------------------------------------------------
# ToolEvent dataclass
# ---------------------------------------------------------------------------


def test_tool_event_call_fields() -> None:
    event = ToolEvent(
        outcome="call",
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "echo hi"},
    )
    assert event.outcome == "call"
    assert event.bot_name == "Loom"
    assert event.tool_name == "run_shell"
    assert event.arguments == {"command": "echo hi"}
    assert event.detail is None


def test_tool_event_blocked_fields() -> None:
    event = ToolEvent(
        outcome="blocked",
        bot_name="Loom",
        tool_name="write_file",
        arguments={"path": "../secret"},
        detail="path escapes sandbox",
    )
    assert event.outcome == "blocked"
    assert event.detail == "path escapes sandbox"


def test_tool_event_error_fields() -> None:
    event = ToolEvent(
        outcome="error",
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "bad"},
        detail="Error: command not found",
    )
    assert event.outcome == "error"
    assert event.detail == "Error: command not found"


# ---------------------------------------------------------------------------
# LoadEvent dataclass
# ---------------------------------------------------------------------------


def test_load_event_context_fields() -> None:
    event = LoadEvent(
        kind="context",
        bot_name="Lore",
        source="file",
        path="AGENTS.md",
        content="# Project\n...",
    )
    assert event.kind == "context"
    assert event.source == "file"
    assert event.path == "AGENTS.md"


def test_load_event_memory_fields() -> None:
    event = LoadEvent(
        kind="memory",
        bot_name="Aura",
        source="file",
        path="/home/user/.codemoo/memory.md",
        content="User prefers Python.",
    )
    assert event.kind == "memory"
    assert event.source == "file"


# ---------------------------------------------------------------------------
# CommentatorBot happy path
# ---------------------------------------------------------------------------


class _MockBackend:
    def __init__(self, response: str = "commentary text") -> None:
        self._response = response
        self.calls: list[list[Message]] = []

    async def complete(self, messages: list[Message], tools: object = None) -> str:
        self.calls.append(messages)
        return self._response


@pytest.mark.asyncio
async def test_comment_tool_call_posts_message_with_persona_sender() -> None:
    backend = _MockBackend(response="Oh wow, a shell command!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolEvent(
        outcome="call",
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "ls"},
    )
    await bot.comment(event)

    assert len(received) == 1
    assert received[0].sender in _TEST_PERSONA_NAMES
    assert "Oh wow, a shell command!" in received[0].text
    assert "run_shell" in received[0].text
    assert "[dim]" in received[0].text


@pytest.mark.asyncio
async def test_comment_passes_event_info_in_prompt() -> None:
    backend = _MockBackend()
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    bot.register(lambda _: None)

    event = ToolEvent(
        outcome="call",
        bot_name="Ash",
        tool_name="read_file",
        arguments={"path": "README.md"},
    )
    await bot.comment(event)

    assert backend.calls
    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "Ash" in user_msg.content
    assert "read_file" in user_msg.content


@pytest.mark.asyncio
async def test_comment_blocked_uses_blocked_template() -> None:
    backend = _MockBackend(response="Security!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    bot.register(lambda _: None)

    event = ToolEvent(
        outcome="blocked",
        bot_name="Cato",
        tool_name="write_file",
        arguments={"path": "../secret"},
        detail="path escapes sandbox",
    )
    await bot.comment(event)

    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "path escapes sandbox" in user_msg.content


@pytest.mark.asyncio
async def test_comment_load_context_uses_context_template() -> None:
    backend = _MockBackend(response="Loaded context!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    bot.register(lambda _: None)

    event = LoadEvent(
        kind="context",
        bot_name="Lore",
        source="file",
        path="AGENTS.md",
        content="# Project context",
    )
    await bot.comment(event)

    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "AGENTS.md" in user_msg.content


@pytest.mark.asyncio
async def test_comment_load_memory_uses_memory_template() -> None:
    backend = _MockBackend(response="Remembered!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    bot.register(lambda _: None)

    event = LoadEvent(
        kind="memory",
        bot_name="Aura",
        source="file",
        path="memory.md",
        content="User likes cats.",
    )
    await bot.comment(event)

    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "memory.md" in user_msg.content


# ---------------------------------------------------------------------------
# Streik fallback
# ---------------------------------------------------------------------------


class _FailingBackend:
    async def complete(self, messages: list[Message], tools: object = None) -> str:
        msg = "LLM exploded"
        raise RuntimeError(msg)


@pytest.mark.asyncio
async def test_streik_fallback_on_llm_error() -> None:
    bot = CommentatorBot(
        llm=_FailingBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolEvent(
        outcome="call",
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "ls"},
    )
    await bot.comment(event)  # must not raise

    assert len(received) == 1
    assert received[0].sender == _STREIK_NAME


@pytest.mark.asyncio
async def test_streik_fallback_text_contains_tool_name_and_bot_name() -> None:
    bot = CommentatorBot(
        llm=_FailingBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolEvent(
        outcome="call",
        bot_name="Ash",
        tool_name="read_file",
        arguments={"path": "SCRIPT.md"},
    )
    await bot.comment(event)

    text = received[0].text
    assert "Ash" in text
    assert "read_file" in text
    assert "SCRIPT.md" in text


# ---------------------------------------------------------------------------
# dispatch_tool emits ToolEvent; bots no longer emit directly
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
    def __init__(self, step: str | ToolUse) -> None:
        self._step = step

    async def complete(
        self, messages: list[Message], tools: object = None
    ) -> str | ToolUse:
        if tools is not None:
            return self._step
        return "done"


@pytest.mark.asyncio
async def test_single_turn_tool_bot_commentator_called_via_dispatch() -> None:
    """dispatch_tool (not the bot) emits the ToolEvent; commentator still fires."""
    received_events: list[object] = []

    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(side_effect=received_events.append)

    bot = SingleTurnToolBot(
        name="Ash",
        emoji="🐚",
        llm=_SingleStepBackend(_TOOL_USE),
        tools=[run_shell],
        instructions="",
        commentator=mock_commentator,
    )

    await bot.on_message(user_ctx("run it"))

    assert len(received_events) == 1
    assert isinstance(received_events[0], ToolEvent)
    assert received_events[0].outcome == "call"


# ---------------------------------------------------------------------------
# AgentBot calls commentator on each tool call in a multi-step loop
# ---------------------------------------------------------------------------


class _MultiStepBackend:
    def __init__(self, steps: list[str | ToolUse]) -> None:
        self._steps = list(steps)

    async def complete(
        self, messages: list[Message], tools: object = None
    ) -> str | ToolUse:
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
    comment_events: list[object] = []
    mock_commentator = AsyncMock()
    mock_commentator.comment = AsyncMock(side_effect=comment_events.append)

    backend = _MultiStepBackend([_tool_use("c1"), _tool_use("c2"), "all done"])
    bot = AgentBot(
        name="Loom",
        emoji="🌀",
        llm=backend,
        tools=[run_shell],
        instructions="You are a helpful assistant.",
        commentator=mock_commentator,
    )

    await bot.on_message(user_ctx("do two things"))

    assert len(comment_events) == 2
    assert all(isinstance(e, ToolEvent) for e in comment_events)
    assert all(e.outcome == "call" for e in comment_events)  # ty: ignore[unresolved-attribute]


# ---------------------------------------------------------------------------
# ChatApp._append_to_log fallback for unknown sender
# ---------------------------------------------------------------------------


class _NullBackend:
    async def complete(self, messages: object, tools: object = None) -> str:
        return ""


_HUMAN = HumanParticipant()


def _make_app() -> ChatApp:
    return ChatApp(
        human=_HUMAN,
        participants=[],
        error_bot=ErrorBot(llm=_NullBackend()),
    )


def test_unknown_sender_resolved_to_commentator_class() -> None:
    app = _make_app()
    default = ("\N{SPEECH BALLOON}", "bubble--commentator")
    _, css_class = app._sender_info.get("UnknownPersona", default)
    assert css_class == "bubble--commentator"


def test_known_senders_are_not_affected() -> None:
    app = _make_app()
    _, css_class = app._sender_info[_HUMAN.name]
    assert css_class == "bubble--human"


# ---------------------------------------------------------------------------
# sender_info() and emoji registration
# ---------------------------------------------------------------------------


def test_sender_info_contains_all_personas() -> None:
    bot = CommentatorBot(
        llm=_NullBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    info = bot.sender_info()
    for persona in _TEST_PERSONAS:
        assert persona.name in info
        emoji, css = info[persona.name]
        assert emoji == persona.emoji
        assert css == "bubble--commentator"


def test_sender_info_contains_streik() -> None:
    bot = CommentatorBot(
        llm=_NullBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    info = bot.sender_info()
    assert _STREIK_NAME in info
    _, css = info[_STREIK_NAME]
    assert css == "bubble--commentator"


def test_sender_info_keys_match_injected_personas_plus_streik() -> None:
    bot = CommentatorBot(
        llm=_NullBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    info = bot.sender_info()
    expected = {p.name for p in _TEST_PERSONAS} | {_STREIK_NAME}
    assert set(info.keys()) == expected


def test_chat_app_registers_persona_emojis_when_commentator_provided() -> None:
    bot = CommentatorBot(
        llm=_NullBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    app = ChatApp(
        human=_HUMAN,
        participants=[],
        error_bot=ErrorBot(llm=_NullBackend()),
        commentator_bot=bot,
    )
    for persona in _TEST_PERSONAS:
        assert persona.name in app._sender_info
        emoji, _ = app._sender_info[persona.name]
        assert emoji == persona.emoji


@pytest.mark.asyncio
async def test_display_header_truncates_long_values_with_ellipsis() -> None:
    backend = _MockBackend(response="Nice!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolEvent(
        outcome="call",
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
        bot = CommentatorBot(
            llm=_FailingBackend(), personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
        )
        received: list[ChatMessage] = []
        bot.register(received.append)
        event = ToolEvent(
            outcome="call",
            bot_name="Ash",
            tool_name="read_file",
            arguments={"path": "x.md"},
        )
        await bot.comment(event)
        return received[0]

    msg = asyncio.run(_run())
    assert "[dim]" not in msg.text


@pytest.mark.asyncio
async def test_empty_personas_falls_back_to_streik() -> None:
    bot = CommentatorBot(llm=_MockBackend(), personas=[], templates=_TEST_TEMPLATES)
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ToolEvent(
        outcome="call",
        bot_name="Loom",
        tool_name="run_shell",
        arguments={"command": "ls"},
    )
    await bot.comment(event)

    assert len(received) == 1
    assert received[0].sender == _STREIK_NAME


# ---------------------------------------------------------------------------
# ContextEvent — restart and compact kinds
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_context_event_compact_posts_bubble_with_dim_prefix() -> None:
    backend = _MockBackend(response="Clarity achieved!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ContextEvent(
        kind="compact",
        bot_name="Drop",
        items_affected=8,
        preview="User asked about bugs. Drop identified the issue.",
    )
    await bot.comment(event)

    assert len(received) == 1
    assert received[0].sender in _TEST_PERSONA_NAMES
    assert "Compacted 8 items" in received[0].text
    assert "[dim]" in received[0].text


@pytest.mark.asyncio
async def test_context_event_restart_posts_bubble_with_dim_prefix() -> None:
    backend = _MockBackend(response="All is lost!")
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    received: list[ChatMessage] = []
    bot.register(received.append)

    event = ContextEvent(
        kind="restart",
        bot_name="Drop",
        items_affected=12,
        preview="User: fix it\nDrop: on it",
    )
    await bot.comment(event)

    assert len(received) == 1
    assert received[0].sender in _TEST_PERSONA_NAMES
    assert "Restarted — 12 items dropped" in received[0].text
    assert "[dim]" in received[0].text


@pytest.mark.asyncio
async def test_context_event_uses_correct_template_key() -> None:
    backend = _MockBackend()
    bot = CommentatorBot(
        llm=backend, personas=_TEST_PERSONAS, templates=_TEST_TEMPLATES
    )
    bot.register(lambda _: None)

    event = ContextEvent(
        kind="compact",
        bot_name="Drop",
        items_affected=5,
        preview="Decisions logged.",
    )
    await bot.comment(event)

    user_msg = next(m for m in backend.calls[0] if m.role == "user")
    assert "Drop" in user_msg.content
    assert "5" in user_msg.content
    assert "Decisions logged." in user_msg.content
