"""Tests for GuardBot, GuardDecision types, and ApprovalRequest."""

from datetime import UTC, datetime

import pytest

from codemoo.core.backend import Message, TextResponse, ToolUse
from codemoo.core.bots.guard_bot import ApprovalRequest, Approved, Denied, GuardBot
from codemoo.core.message import ChatMessage
from codemoo.core.tools import ToolDef, ToolParam, run_shell

_TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _msg(sender: str, text: str) -> ChatMessage:
    return ChatMessage(sender=sender, text=text, timestamp=_TS)


def _tool_use(name: str = "run_shell", call_id: str = "c1") -> ToolUse:
    arguments = {"command": "echo hi"} if name == "run_shell" else {"path": "f.py"}
    assistant_msg = Message(
        role="assistant",
        content="",
        tool_calls_json=f'[{{"id":"{call_id}","type":"function","function":{{"name":"{name}","arguments":"{{}}"}}}}]',
    )
    return ToolUse(
        name=name, arguments=arguments, call_id=call_id, assistant_message=assistant_msg
    )


class _SequentialBackend:
    def __init__(self, steps: list[TextResponse | ToolUse]) -> None:
        self._steps = list(steps)
        self.step_calls: list[list[Message]] = []

    async def complete(self, messages: list[Message]) -> str:
        pytest.fail("GuardBot should never call complete()")

    async def complete_step(
        self, messages: list[Message], tools: list[ToolDef]
    ) -> TextResponse | ToolUse:
        self.step_calls.append(list(messages))
        return self._steps.pop(0)


_safe_tool = ToolDef(
    name="read_file",
    description="Safe dummy.",
    parameters=[ToolParam(name="path", description="path")],
    fn=lambda path: f"contents of {path}",
    requires_approval=False,
)


def _make_bot(backend: _SequentialBackend) -> GuardBot:
    return GuardBot(
        name="Cato",
        emoji="🔒",
        llm=backend,
        tools=[run_shell, _safe_tool],
        instructions="You are a helpful assistant.",
    )


# ---------------------------------------------------------------------------
# GuardDecision types
# ---------------------------------------------------------------------------


def test_approved_is_frozen_dataclass() -> None:
    a = Approved()
    assert isinstance(a, Approved)


def test_denied_reason_defaults_to_none() -> None:
    d = Denied()
    assert d.reason is None


def test_denied_carries_reason() -> None:
    d = Denied(reason="use archive/ instead")
    assert d.reason == "use archive/ instead"


def test_approval_request_fields() -> None:
    tu = _tool_use()
    req = ApprovalRequest(bot_name="Cato", tool_use=tu)
    assert req.bot_name == "Cato"
    assert req.tool_use is tu


# ---------------------------------------------------------------------------
# GuardBot protocol
# ---------------------------------------------------------------------------


def test_guard_bot_is_not_human() -> None:
    backend = _SequentialBackend([TextResponse(text="hi")])
    assert _make_bot(backend).is_human is False


# ---------------------------------------------------------------------------
# Default ask_fn approves without prompting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_default_ask_fn_approves_dangerous_tool() -> None:
    backend = _SequentialBackend([_tool_use("run_shell"), TextResponse(text="done")])
    bot = _make_bot(backend)

    reply = await bot.on_message(_msg("You", "run something"), [])

    assert reply is not None
    assert reply.text == "done"


# ---------------------------------------------------------------------------
# Safe tools bypass the gate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_safe_tool_bypasses_gate() -> None:
    ask_calls: list[ApprovalRequest] = []

    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        ask_calls.append(req)
        return Approved()

    backend = _SequentialBackend([_tool_use("read_file"), TextResponse(text="done")])
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "read the file"), [])

    assert len(ask_calls) == 0


# ---------------------------------------------------------------------------
# Dangerous tools invoke ask_fn
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dangerous_tool_invokes_ask_fn() -> None:
    ask_calls: list[ApprovalRequest] = []

    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        ask_calls.append(req)
        return Approved()

    backend = _SequentialBackend([_tool_use("run_shell"), TextResponse(text="done")])
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "run something"), [])

    assert len(ask_calls) == 1
    assert ask_calls[0].bot_name == "Cato"
    assert ask_calls[0].tool_use.name == "run_shell"


# ---------------------------------------------------------------------------
# Approved: tool runs, output fed back to LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_approved_tool_runs_and_output_in_context() -> None:
    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        return Approved()

    backend = _SequentialBackend([_tool_use("run_shell"), TextResponse(text="done")])
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "run it"), [])

    second_call = backend.step_calls[1]
    tool_msgs = [m for m in second_call if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert "denied" not in tool_msgs[0].content.lower()


# ---------------------------------------------------------------------------
# Denied (plain): denial message fed back to LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_plain_deny_produces_standard_message() -> None:
    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        return Denied()

    backend = _SequentialBackend([_tool_use("run_shell"), TextResponse(text="ok")])
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "run it"), [])

    second_call = backend.step_calls[1]
    tool_msgs = [m for m in second_call if m.role == "tool"]
    assert len(tool_msgs) == 1
    assert (
        tool_msgs[0].content == "The user denied this tool call."
        " Do not attempt it again — move on to the next step."
    )


# ---------------------------------------------------------------------------
# Denied with reason: reason included in message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deny_with_reason_includes_reason() -> None:
    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        return Denied(reason="use archive/ instead")

    backend = _SequentialBackend([_tool_use("run_shell"), TextResponse(text="ok")])
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "run it"), [])

    second_call = backend.step_calls[1]
    tool_msgs = [m for m in second_call if m.role == "tool"]
    assert tool_msgs[0].content == "Tool call denied: use archive/ instead"


# ---------------------------------------------------------------------------
# Loop continues after denial
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_loop_continues_after_denial() -> None:
    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        return Denied(reason="no")

    backend = _SequentialBackend(
        [
            _tool_use("run_shell"),
            _tool_use("run_shell", "c2"),
            TextResponse(text="gave up"),
        ]
    )
    bot = _make_bot(backend)
    bot.register_guard(ask_fn)

    reply = await bot.on_message(_msg("You", "run it twice"), [])

    assert reply is not None
    assert reply.text == "gave up"
    assert len(backend.step_calls) == 3


# ---------------------------------------------------------------------------
# Unused safe tool (read_file) in tools list with dangerous tool also present
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_only_dangerous_tools_require_approval() -> None:
    safe_tool = ToolDef(
        name="safe_op",
        description="Safe.",
        parameters=[ToolParam(name="x", description="x")],
        fn=lambda **_: "safe result",
        requires_approval=False,
    )
    dangerous_tool = ToolDef(
        name="danger_op",
        description="Dangerous.",
        parameters=[ToolParam(name="x", description="x")],
        fn=lambda **_: "danger result",
        requires_approval=True,
    )
    ask_calls: list[str] = []

    async def ask_fn(req: ApprovalRequest) -> Approved | Denied:
        ask_calls.append(req.tool_use.name)
        return Approved()

    safe_use = ToolUse(
        name="safe_op",
        arguments={"x": "v"},
        call_id="s1",
        assistant_message=Message(role="assistant", content="", tool_calls_json="[]"),
    )
    danger_use = ToolUse(
        name="danger_op",
        arguments={"x": "v"},
        call_id="d1",
        assistant_message=Message(role="assistant", content="", tool_calls_json="[]"),
    )

    backend = _SequentialBackend([safe_use, danger_use, TextResponse(text="done")])
    bot = GuardBot(
        name="Cato",
        emoji="🔒",
        llm=backend,
        tools=[safe_tool, dangerous_tool],
        instructions="You are a helpful assistant.",
    )
    bot.register_guard(ask_fn)

    await bot.on_message(_msg("You", "do things"), [])

    assert ask_calls == ["danger_op"]
