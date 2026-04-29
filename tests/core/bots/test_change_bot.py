from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.change_bot import ChangeBot
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, run_shell

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


def _make_assistant_msg() -> Message:
    args = '{\\"command\\":\\"echo hi\\"}'
    return Message(
        role="assistant",
        content="",
        tool_calls_json=(
            f'[{{"id":"c1","type":"function","function":'
            f'{{"name":"run_shell","arguments":"{args}"}}}}'
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
def tool_backend() -> _MockBackend:
    return _MockBackend(
        step_result=ToolUse(
            name="run_shell",
            arguments={"command": "echo hi"},
            call_id="c1",
            assistant_message=_make_assistant_msg(),
        ),
        complete_response="Command output received.",
    )


@pytest.fixture
def bot_text(text_backend: _MockBackend) -> ChangeBot:
    return ChangeBot(
        name="A",
        emoji="\N{HAMMER}",
        llm=text_backend,
        tools=[run_shell],
        instructions="You can execute shell commands and write files using your tools.",
    )


@pytest.fixture
def bot_tool(tool_backend: _MockBackend) -> ChangeBot:
    return ChangeBot(
        name="A",
        emoji="\N{HAMMER}",
        llm=tool_backend,
        tools=[run_shell],
        instructions="You can execute shell commands and write files using your tools.",
    )


def test_change_bot_is_not_human(bot_text: ChangeBot) -> None:
    assert bot_text.is_human is False


@pytest.mark.asyncio
async def test_text_response_path_reply_sender(bot_text: ChangeBot) -> None:
    reply = await bot_text.on_message(_msg("You", "hi"), [])

    assert reply is not None
    assert reply.sender == "A"
    assert reply.text == "plain reply"


@pytest.mark.asyncio
async def test_text_response_path_no_complete_call(
    bot_text: ChangeBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    assert len(text_backend.step_calls) == 1
    assert text_backend.complete_calls == []


@pytest.mark.asyncio
async def test_tool_use_path_runs_command_and_replies(
    bot_tool: ChangeBot, tool_backend: _MockBackend
) -> None:
    reply = await bot_tool.on_message(_msg("You", "run echo hi"), [])

    assert len(tool_backend.step_calls) == 1
    assert len(tool_backend.complete_calls) == 1
    assert reply is not None
    assert reply.sender == "A"
    assert reply.text == "Command output received."


@pytest.mark.asyncio
async def test_tool_use_path_follow_up_includes_shell_output(
    bot_tool: ChangeBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "run echo hi"), [])

    follow_up = tool_backend.complete_calls[0]
    tool_msgs = [m for m in follow_up if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_complete_step_receives_run_shell_tool(
    bot_tool: ChangeBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(_msg("You", "hi"), [])

    _, tools_sent = tool_backend.step_calls[0]
    assert tools_sent == [run_shell]


@pytest.mark.asyncio
async def test_system_prompt_mentions_shell_commands(
    bot_text: ChangeBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(_msg("You", "hi"), [])

    context, _ = text_backend.step_calls[0]
    assert context[0].role == "system"
    assert "shell commands" in context[0].content
