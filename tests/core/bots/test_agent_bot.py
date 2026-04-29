from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.agent_bot import AgentBot
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, run_shell

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


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

    def __init__(self, steps: list[TextResponse | ToolUse]) -> None:
        self._steps = list(steps)
        self.step_calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        pytest.fail("AgentBot should never call complete()")

    async def complete_step(
        self,
        messages: list[Message],
        tools: list[ToolDef],
    ) -> TextResponse | ToolUse:
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


def test_agent_bot_is_not_human() -> None:
    backend = _SequentialBackend([TextResponse(text="hi")])
    assert _make_bot(backend).is_human is False


@pytest.mark.asyncio
async def test_immediate_text_response_no_tool_call() -> None:
    backend = _SequentialBackend([TextResponse(text="plain reply")])
    bot = _make_bot(backend)

    reply = await bot.on_message(_msg("You", "hello"), [])

    assert reply is not None
    assert reply.sender == "Loom"
    assert reply.text == "plain reply"
    assert len(backend.step_calls) == 1


@pytest.mark.asyncio
async def test_single_tool_call_then_text_response() -> None:
    backend = _SequentialBackend([_tool_use("c1"), TextResponse(text="done")])
    bot = _make_bot(backend)

    reply = await bot.on_message(_msg("You", "run echo hi"), [])

    assert reply is not None
    assert reply.sender == "Loom"
    assert reply.text == "done"
    assert len(backend.step_calls) == 2


@pytest.mark.asyncio
async def test_single_tool_call_context_fed_back() -> None:
    backend = _SequentialBackend([_tool_use("c1"), TextResponse(text="done")])
    bot = _make_bot(backend)

    await bot.on_message(_msg("You", "run echo hi"), [])

    second_call_msgs = backend.step_calls[1]
    tool_msgs = [m for m in second_call_msgs if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0].tool_call_id == "c1"


@pytest.mark.asyncio
async def test_two_sequential_tool_calls_then_text() -> None:
    backend = _SequentialBackend(
        [_tool_use("c1"), _tool_use("c2"), TextResponse(text="all done")]
    )
    bot = _make_bot(backend)

    reply = await bot.on_message(_msg("You", "do two things"), [])

    assert reply is not None
    assert reply.text == "all done"
    assert len(backend.step_calls) == 3


@pytest.mark.asyncio
async def test_two_tool_calls_both_outputs_in_final_context() -> None:
    backend = _SequentialBackend(
        [_tool_use("c1"), _tool_use("c2"), TextResponse(text="all done")]
    )
    bot = _make_bot(backend)

    await bot.on_message(_msg("You", "do two things"), [])

    third_call_msgs = backend.step_calls[2]
    tool_msgs = [m for m in third_call_msgs if m.role == "tool"]
    call_ids = {m.tool_call_id for m in tool_msgs}
    assert call_ids == {"c1", "c2"}
