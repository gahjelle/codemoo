import pytest

from codemoo.core.backend import Message, ToolUse
from codemoo.core.bots.tool_bot import ToolBot
from codemoo.core.tools import ToolDef, reverse_string

from .conftest import user_ctx


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
    """Returns step_result when tools provided, complete_response for follow-ups."""

    def __init__(
        self,
        step_result: str | ToolUse,
        complete_response: str = "final answer",
    ) -> None:
        self.step_result = step_result
        self.complete_response = complete_response
        self.complete_calls: list[list[Message]] = []
        self.step_calls: list[tuple[list[Message], list[ToolDef]]] = []

    async def complete(
        self, messages: list[Message], tools: list[ToolDef] | None = None
    ) -> str | ToolUse:
        if tools is not None:
            self.step_calls.append((list(messages), list(tools)))
            return self.step_result
        self.complete_calls.append(list(messages))
        return self.complete_response


@pytest.fixture
def text_backend() -> _MockBackend:
    return _MockBackend(step_result="plain reply")


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
        llm=text_backend,
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
        llm=tool_backend,
        tools=[reverse_string],
        instructions="You have tools available. Use them when they would help.",
    )


@pytest.mark.asyncio
async def test_text_response_path_calls_complete_with_tools(
    bot_text: ToolBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(user_ctx("hi"))

    assert len(text_backend.step_calls) == 1
    assert text_backend.complete_calls == []


@pytest.mark.asyncio
async def test_text_response_path_reply_sender(bot_text: ToolBot) -> None:
    from codemoo.core.context_items import AssistantMessageContent

    [item] = await bot_text.on_message(user_ctx("hi"))

    assert isinstance(item.content, AssistantMessageContent)
    assert item.content.text == "plain reply"


@pytest.mark.asyncio
async def test_tool_use_path_invokes_tool_and_calls_complete(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    from codemoo.core.context_items import AssistantMessageContent

    new_items = await bot_tool.on_message(user_ctx("reverse hello"))

    assert len(tool_backend.step_calls) == 1
    assert len(tool_backend.complete_calls) == 1
    assert isinstance(new_items[-1].content, AssistantMessageContent)
    assert new_items[-1].content.text == "The reversed string is: olleh"


@pytest.mark.asyncio
async def test_tool_use_path_follow_up_includes_tool_result(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(user_ctx("reverse hello"))

    follow_up = tool_backend.complete_calls[0]
    tool_msgs = [m for m in follow_up if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].content == "olleh"
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_complete_receives_tool_list(
    bot_tool: ToolBot, tool_backend: _MockBackend
) -> None:
    await bot_tool.on_message(user_ctx("hi"))

    _, tools_sent = tool_backend.step_calls[0]
    assert tools_sent == [reverse_string]


@pytest.mark.asyncio
async def test_tool_use_path_empty_complete_uses_fallback(
    empty_backend: _MockBackend,
) -> None:
    from codemoo.core.context_items import AssistantMessageContent

    bot = ToolBot(
        name="Telo",
        emoji="\N{WRENCH}",
        llm=empty_backend,
        tools=[reverse_string],
        instructions="You have tools available.",
    )
    new_items = await bot.on_message(user_ctx("reverse hello"))

    assert isinstance(new_items[-1].content, AssistantMessageContent)
    assert new_items[-1].content.text == "(tool executed, process interrupted)"


@pytest.mark.asyncio
async def test_system_prompt_forwarded(
    bot_text: ToolBot, text_backend: _MockBackend
) -> None:
    await bot_text.on_message(user_ctx("hi"))

    context, _ = text_backend.step_calls[0]
    assert context[0].role == "system"
    assert context[0].content == bot_text.instructions
