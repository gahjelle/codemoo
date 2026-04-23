"""Tests for ChatApp demo_position parameter and Ctrl-N key handling."""

import pytest

from codemoo.chat.app import ChatApp
from codemoo.chat.demo_header import DemoHeader
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import HumanParticipant


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""


def _make_app(demo_position: tuple[int, int] | None = None) -> ChatApp:
    human = HumanParticipant()
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    error_bot = ErrorBot(backend=_MockBackend())  # type: ignore[arg-type]
    return ChatApp(
        participants=[human, bot],
        error_bot=error_bot,
        demo_position=demo_position,
    )


@pytest.mark.asyncio
async def test_no_demo_header_without_demo_position() -> None:
    async with _make_app(demo_position=None).run_test() as pilot:
        assert not pilot.app.query(DemoHeader)


@pytest.mark.asyncio
async def test_demo_header_present_with_demo_position() -> None:
    async with _make_app(demo_position=(1, 8)).run_test() as pilot:
        assert pilot.app.query_one(DemoHeader)


@pytest.mark.asyncio
async def test_ctrl_n_ignored_without_demo_position() -> None:
    async with _make_app(demo_position=None).run_test() as pilot:
        await pilot.press("ctrl+n")
        assert pilot.app.return_value is None


@pytest.mark.asyncio
async def test_ctrl_n_exits_with_next_in_demo_mode() -> None:
    async with _make_app(demo_position=(1, 8)).run_test() as pilot:
        await pilot.press("ctrl+n")

    assert pilot.app.return_value == "next"
