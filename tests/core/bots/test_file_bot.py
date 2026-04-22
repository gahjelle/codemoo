from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.file_bot import FileBot
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, read_file

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


def _make_assistant_msg() -> Message:
    args = '{\\"path\\":\\"/some/file.txt\\"}'
    return Message(
        role="assistant",
        content="",
        tool_calls_json=(
            f'[{{"id":"c1","type":"function","function":'
            f'{{"name":"read_file","arguments":"{args}"}}}}'
            f"]"
        ),
    )


class _MockBackend:
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
def tool_backend(tmp_path: pytest.TempPathFactory) -> _MockBackend:
    return _MockBackend(
        step_result=ToolUse(
            name="read_file",
            arguments={"path": __file__},
            call_id="c1",
            assistant_message=_make_assistant_msg(),
        ),
        complete_response="Here are the file contents.",
    )


@pytest.fixture
def bot_text(text_backend: _MockBackend) -> FileBot:
    return FileBot(
        name="R",
        emoji="\N{FILE FOLDER}",
        backend=text_backend,
        human_name="You",
        tools=[read_file],
    )


@pytest.fixture
def bot_tool(tool_backend: _MockBackend) -> FileBot:
    return FileBot(
        name="R",
        emoji="\N{FILE FOLDER}",
        backend=tool_backend,
        human_name="You",
        tools=[read_file],
    )


def test_file_bot_is_not_human(bot_text: FileBot) -> None:
    assert bot_text.is_human is False


@pytest.mark.asyncio
async def test_text_response_path_reply_sender(bot_text: FileBot) -> None:
    reply = await bot_text.on_message(_msg("You", "hi"), [])

    assert reply is not None
    assert reply.sender == "R"
    assert reply.text == "plain reply"


@pytest.mark.asyncio
async def test_text_response_path_no_complete_call(
    bot_text: FileBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    assert len(text_backend.step_calls) == 1
    assert text_backend.complete_calls == []


@pytest.mark.asyncio
async def test_tool_use_path_reads_file_and_replies(
    bot_tool: FileBot, tool_backend: _MockBackend
) -> None:
    reply = await bot_tool.on_message(_msg("You", "read the file"), [])

    assert len(tool_backend.step_calls) == 1
    assert len(tool_backend.complete_calls) == 1
    assert reply is not None
    assert reply.sender == "R"
    assert reply.text == "Here are the file contents."


@pytest.mark.asyncio
async def test_tool_use_path_follow_up_includes_file_contents(
    bot_tool: FileBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "read the file"), [])

    follow_up = tool_backend.complete_calls[0]
    tool_msgs = [m for m in follow_up if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_complete_step_receives_read_file_tool(
    bot_tool: FileBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "hi"), [])

    _, tools_sent = tool_backend.step_calls[0]
    assert tools_sent == [read_file]


@pytest.mark.asyncio
async def test_system_prompt_mentions_read_file(
    bot_text: FileBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    context, _ = text_backend.step_calls[0]
    assert context[0].role == "system"
    assert "read_file" in context[0].content
