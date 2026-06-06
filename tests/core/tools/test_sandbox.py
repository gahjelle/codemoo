"""Tests for dispatch_tool, make_file_validator, and make_shell_validator."""

import asyncio
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

from codemoo.core.commentator import ToolEvent
from codemoo.core.tools import ToolDef, ToolParam, dispatch_tool
from codemoo.core.tools.files import make_file_validator
from codemoo.core.tools.shell import make_shell_validator


def _make_tool(
    fn: Callable[..., object], *, validate: Callable[..., str | None] | None = None
) -> ToolDef:
    return ToolDef(
        name="test_tool",
        description="test",
        parameters=[ToolParam(name="x", description="x")],
        fn=fn,
        validate=validate,
    )


# ---------------------------------------------------------------------------
# dispatch_tool
# ---------------------------------------------------------------------------


def test_dispatch_tool_no_validate_calls_fn() -> None:
    called: list[str] = []

    async def fn(x: str) -> str:
        called.append(x)
        return "ok"

    tool = _make_tool(fn)
    result = asyncio.run(dispatch_tool(tool, {"x": "hello"}, "Bot", None))
    assert result == "ok"
    assert called == ["hello"]


def test_dispatch_tool_validate_returns_none_calls_fn() -> None:
    async def fn(**_: object) -> str:
        return "fn_result"

    tool = _make_tool(fn, validate=lambda **_: None)
    result = asyncio.run(dispatch_tool(tool, {"x": "v"}, "Bot", None))
    assert result == "fn_result"


def test_dispatch_tool_validate_blocks_fn_not_called() -> None:
    fn_called: list[bool] = []

    async def fn(**_: object) -> str:
        fn_called.append(True)
        return "bad"

    tool = _make_tool(fn, validate=lambda **_: "Blocked: test reason")
    result = asyncio.run(dispatch_tool(tool, {"x": "v"}, "Bot", None))
    assert result == "Blocked: test reason"
    assert not fn_called


def test_dispatch_tool_emits_blocked_event() -> None:
    events: list[object] = []

    async def fake_comment(event: object) -> None:
        events.append(event)

    commentator = MagicMock()
    commentator.comment = fake_comment

    tool = _make_tool(lambda **_: "bad", validate=lambda **_: "path escape")
    asyncio.run(dispatch_tool(tool, {"x": "v"}, "MyBot", commentator))

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ToolEvent)
    assert event.outcome == "blocked"
    assert event.bot_name == "MyBot"
    assert event.tool_name == "test_tool"
    assert event.detail == "path escape"


def test_dispatch_tool_emits_call_event_on_success() -> None:
    events: list[object] = []

    async def fake_comment(event: object) -> None:
        events.append(event)

    commentator = MagicMock()
    commentator.comment = fake_comment

    async def fn(**_: object) -> str:
        return "ok"

    tool = _make_tool(fn)
    asyncio.run(dispatch_tool(tool, {"x": "v"}, "MyBot", commentator))

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ToolEvent)
    assert event.outcome == "call"
    assert event.bot_name == "MyBot"


def test_dispatch_tool_blocked_emits_no_call_event() -> None:
    """Blocked call must not emit a 'call' event — only 'blocked'."""
    events: list[object] = []

    async def fake_comment(event: object) -> None:
        events.append(event)

    commentator = MagicMock()
    commentator.comment = fake_comment

    async def fn(**_: object) -> str:
        return "bad"

    tool = _make_tool(fn, validate=lambda **_: "blocked reason")
    asyncio.run(dispatch_tool(tool, {"x": "v"}, "MyBot", commentator))

    assert len(events) == 1
    assert events[0].outcome == "blocked"  # ty: ignore[unresolved-attribute]


def test_dispatch_tool_blocked_no_commentator_returns_error() -> None:
    async def fn(**_: object) -> str:
        return "fn"

    tool = _make_tool(fn, validate=lambda **_: "error msg")
    result = asyncio.run(dispatch_tool(tool, {"x": "v"}, "Bot", None))
    assert result == "error msg"


# ---------------------------------------------------------------------------
# make_file_validator
# ---------------------------------------------------------------------------


def test_file_validator_allows_path_within_session(tmp_path: Path) -> None:
    validator = make_file_validator(tmp_path)
    assert validator(path="subdir/file.txt") is None


def test_file_validator_blocks_traversal(tmp_path: Path) -> None:
    validator = make_file_validator(tmp_path)
    result = validator(path="../secret.txt")
    assert result is not None
    assert "../secret.txt" in result or "secret" in result
    assert str(tmp_path.resolve()) in result


def test_file_validator_blocks_absolute_outside(tmp_path: Path) -> None:
    validator = make_file_validator(tmp_path)
    result = validator(path="/etc/passwd")
    assert result is not None
    assert str(tmp_path.resolve()) in result


def test_file_validator_allows_absolute_within_session(tmp_path: Path) -> None:
    validator = make_file_validator(tmp_path)
    inside = str(tmp_path / "myfile.txt")
    assert validator(path=inside) is None


def test_file_validator_allows_dot_relative(tmp_path: Path) -> None:
    validator = make_file_validator(tmp_path)
    assert validator(path="./file.txt") is None


# ---------------------------------------------------------------------------
# make_shell_validator
# ---------------------------------------------------------------------------


def test_shell_validator_allows_simple_command(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    assert validator(command="pytest tests/") is None


def test_shell_validator_allows_dotslash(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    assert validator(command="./run.sh") is None


def test_shell_validator_blocks_absolute_path_token(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    result = validator(command="cat /etc/passwd")
    assert result is not None
    assert "/etc/passwd" in result


def test_shell_validator_blocks_traversal_token(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    result = validator(command="ls ../")
    assert result is not None
    assert "../" in result


def test_shell_validator_blocks_flag_with_absolute_value(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    result = validator(command="python --config=/etc/app.conf")
    assert result is not None
    assert "/etc/app.conf" in result


def test_shell_validator_blocks_unparseable_command(tmp_path: Path) -> None:
    validator = make_shell_validator(tmp_path)
    result = validator(command="echo 'unclosed")
    assert result is not None
