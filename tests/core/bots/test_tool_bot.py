from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.tool_bot import ToolBot
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, reverse_string

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


def _make_assistant_msg() -> Message:
    args = '{\\"text\\":\\"hi\\"}'
    return Message(
        role="assistant",
        content="",
        tool_calls_json=(
            f'[{{"id":"c1","type":"function","function":'
            f'{{"name":"reverse_string","arguments":"{args}"}}}}'
            f"]"
        ),
    )


class _MockBackend:
    """Captures calls; step_result controls what complete_step returns."""

    def __init__(
        self,
        step_result: TextResponse | ToolUse,
        complete_response: str = "final answer",
    ) -> None:
        self.step_result = step_result
        self.complete_response = complete_response
        self.complete_calls: list[list[Message]] = []
        self.step_calls: list[tuple[list[Message], list[ToolDef]]] = []

    async def complete(self, messages: list[Message]) -> str:
        self.complete_calls.append(list(messages))
        return self.complete_response

    async def complete_step(
        self, messages: list[Message], tools: list[ToolDef]
    ) -> TextResponse | ToolUse:
        self.step_calls.append((list(messages), list(tools)))
        return self.step_result


@pytest.fixture
def text_backend() -> _MockBackend:
    return _MockBackend(step_result=TextResponse(text="plain reply"))


@pytest.fixture
def tool_backend() -> _MockBackend:
    return _MockBackend(
        step_result=ToolUse(
            name="reverse_string",
            arguments={"text": "hello"},
            call_id="c1",
            assistant_message=_make_assistant_msg(),
        ),
        complete_response="The reversed string is: olleh",
    )


@pytest.fixture
def bot_text(text_backend: _MockBackend) -> ToolBot:
    return ToolBot(
        name="Telo",
        emoji="\N{WRENCH}",
        backend=text_backend,
        tools=[reverse_string],
        instructions="You have tools available. Use them when they would help.",
    )


@pytest.fixture
def empty_backend() -> _MockBackend:
    return _MockBackend(
        step_result=ToolUse(
            name="reverse_string",
            arguments={"text": "hello"},
            call_id="c1",
            assistant_message=_make_assistant_msg(),
        ),
        complete_response="",
    )


@pytest.fixture
def bot_tool(tool_backend: _MockBackend) -> ToolBot:
    return ToolBot(
        name="Telo",
        emoji="\N{WRENCH}",
        backend=tool_backend,
        tools=[reverse_string],
        instructions="You have tools available. Use them when they would help.",
    )


def test_tool_bot_is_not_human(bot_text: ToolBot) -> None:
    assert bot_text.is_human is False


@pytest.mark.asyncio
async def test_text_response_path_calls_complete_step(
    bot_text: ToolBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    assert len(text_backend.step_calls) == 1
    assert text_backend.complete_calls == []


@pytest.mark.asyncio
async def test_text_response_path_reply_sender(bot_text: ToolBot) -> None:
    reply = await bot_text.on_message(_msg("You", "hi"), [])

    assert reply is not None
    assert reply.sender == "Telo"
    assert reply.text == "plain reply"


@pytest.mark.asyncio
async def test_tool_use_path_invokes_tool_and_calls_complete(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    reply = await bot_tool.on_message(_msg("You", "reverse hello"), [])

    assert len(tool_backend.step_calls) == 1
    assert len(tool_backend.complete_calls) == 1
    assert reply is not None
    assert reply.sender == "Telo"
    assert reply.text == "The reversed string is: olleh"


@pytest.mark.asyncio
async def test_tool_use_path_follow_up_includes_tool_result(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "reverse hello"), [])

    follow_up = tool_backend.complete_calls[0]
    tool_msgs = [m for m in follow_up if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].content == "olleh"
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_complete_step_receives_tool_list(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "hi"), [])

    _, tools_sent = tool_backend.step_calls[0]
    assert tools_sent == [reverse_string]


@pytest.mark.asyncio
async def test_tool_use_path_empty_complete_uses_fallback(
    empty_backend: _MockBackend,
) -> None:
    bot = ToolBot(
        name="Telo",
        emoji="\N{WRENCH}",
        backend=empty_backend,
        tools=[reverse_string],
        instructions="You have tools available.",
    )
    reply = await bot.on_message(_msg("You", "reverse hello"), [])

    assert reply is not None
    assert reply.text == "(tool executed, process interrupted)"


@pytest.mark.asyncio
async def test_system_prompt_forwarded(
    bot_text: ToolBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    context, _ = text_backend.step_calls[0]
    assert context[0].role == "system"
    assert context[0].content == bot_text.instructions
