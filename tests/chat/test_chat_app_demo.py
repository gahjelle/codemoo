"""Tests for ChatApp demo_context parameter and Ctrl-N key handling."""

import pytest

from codemoo.chat.app import ChatApp
from codemoo.chat.demo_header import DemoHeader
from codemoo.chat.slides import DemoContext
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import HumanParticipant


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""

    async def complete_step(self, messages: object, tools: object) -> object:
        from codemoo.core.backend import TextResponse

        return TextResponse(text="")


def _make_demo_context(position: tuple[int, int] = (1, 8)) -> DemoContext:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoContext(
        all_bots=[bot],
        prev_bot=None,
        backend=_MockBackend(),  # type: ignore[arg-type]
        position=position,
    )


def _make_app(demo_context: DemoContext | None = None) -> ChatApp:
    human = HumanParticipant()
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    error_bot = ErrorBot(backend=_MockBackend())  # type: ignore[arg-type]
    return ChatApp(
        participants=[human, bot],
        error_bot=error_bot,
        demo_context=demo_context,
    )


class _MockKey:
    def __init__(self, key: str) -> None:
        self.key = key


# --- Header presence: check compose() output without a running Textual app ---


def test_no_demo_header_without_demo_context() -> None:
    app = _make_app(demo_context=None)
    widgets = list(app.compose())
    assert not any(isinstance(w, DemoHeader) for w in widgets)


def test_demo_header_present_with_demo_context() -> None:
    app = _make_app(demo_context=_make_demo_context())
    widgets = list(app.compose())
    assert any(isinstance(w, DemoHeader) for w in widgets)


# --- Ctrl-N key handler: test on_key logic directly without a running Textual app ---


def test_ctrl_n_ignored_without_demo_context() -> None:
    app = _make_app(demo_context=None)
    exits: list[str | None] = []
    app.exit = lambda result=None: exits.append(result)  # type: ignore[method-assign]
    app.on_key(_MockKey("ctrl+n"))  # type: ignore[arg-type]
    assert not exits


def test_ctrl_n_exits_with_next_in_demo_mode() -> None:
    app = _make_app(demo_context=_make_demo_context())
    exits: list[str | None] = []
    app.exit = lambda result=None: exits.append(result)  # type: ignore[method-assign]
    app.on_key(_MockKey("ctrl+n"))  # type: ignore[arg-type]
    assert exits == ["next"]


# --- SlideScreen push on mount: one async test for the slide overlay behavior ---


@pytest.mark.asyncio
async def test_slide_screen_pushed_on_mount_in_demo_mode() -> None:
    from codemoo.chat.slides import SlideScreen

    async with _make_app(demo_context=None).run_test() as pilot:
        assert not pilot.app.query(SlideScreen)
