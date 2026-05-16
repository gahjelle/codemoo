from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, ToolUse
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.tools import ToolDef, run_shell

from .conftest import user_ctx

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _tool_use(call_id: str = "c1") -> ToolUse:
    args = '{\\"command\\":\\"echo hi\\"}'
    assistant_msg = Message(
        role="assistant",
        content="",
        tool_calls_json=(
            f'[{{"id":"{call_id}","type":"function","function":'
            f'{{"name":"run_shell","arguments":"{args}"}}}}'
            f"]"
        ),
    )
    return ToolUse(
        name="run_shell",
        arguments={"command": "echo hi"},
        call_id=call_id,
        assistant_message=assistant_msg,
    )


class _SequentialBackend:
    """Returns step results from a queue, then raises if exhausted."""

    def __init__(self, steps: list[str | ToolUse]) -> None:
        self._steps = list(steps)
        self.step_calls: list[list[Message]] = []

    async def complete(
        self, messages: list[Message], tools: list[ToolDef] | None = None
    ) -> str | ToolUse:
        self.step_calls.append(list(messages))
        return self._steps.pop(0)


def _make_bot(backend: _SequentialBackend) -> AgentBot:
    return AgentBot(
        name="Loom",
        emoji="\N{CYCLONE}",
        llm=backend,
        tools=[run_shell],
        instructions="You are a helpful assistant.",
    )


@pytest.mark.asyncio
async def test_immediate_text_response_no_tool_call() -> None:
    from codemoo.core.context_items import AssistantMessageContent

    backend = _SequentialBackend(["plain reply"])
    bot = _make_bot(backend)

    [item] = await bot.on_message(user_ctx("hello"))

    assert isinstance(item.content, AssistantMessageContent)
    assert item.content.text == "plain reply"
    assert len(backend.step_calls) == 1


@pytest.mark.asyncio
async def test_single_tool_call_then_text_response() -> None:
    from codemoo.core.context_items import AssistantMessageContent

    backend = _SequentialBackend([_tool_use("c1"), "done"])
    bot = _make_bot(backend)

    new_items = await bot.on_message(user_ctx("run echo hi"))

    assert isinstance(new_items[-1].content, AssistantMessageContent)
    assert new_items[-1].content.text == "done"
    assert len(backend.step_calls) == 2


@pytest.mark.asyncio
async def test_single_tool_call_context_fed_back() -> None:
    backend = _SequentialBackend([_tool_use("c1"), "done"])
    bot = _make_bot(backend)

    await bot.on_message(user_ctx("run echo hi"))

    second_call_msgs = backend.step_calls[1]
    tool_msgs = [m for m in second_call_msgs if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_two_sequential_tool_calls_then_text() -> None:
    from codemoo.core.context_items import AssistantMessageContent

    backend = _SequentialBackend([_tool_use("c1"), _tool_use("c2"), "all done"])
    bot = _make_bot(backend)

    new_items = await bot.on_message(user_ctx("do two things"))

    assert isinstance(new_items[-1].content, AssistantMessageContent)
    assert new_items[-1].content.text == "all done"
    assert len(backend.step_calls) == 3


@pytest.mark.asyncio
async def test_two_tool_calls_both_outputs_in_final_context() -> None:
    backend = _SequentialBackend([_tool_use("c1"), _tool_use("c2"), "all done"])
    bot = _make_bot(backend)

    await bot.on_message(user_ctx("do two things"))

    third_call_msgs = backend.step_calls[2]
    tool_msgs = [m for m in third_call_msgs if m.role == "tool"]
    call_ids = {m.tool_call_id for m in tool_msgs}
    assert call_ids == {"c1", "c2"}
