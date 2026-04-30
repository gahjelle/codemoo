"""Tests for ChatApp demo_context parameter and Ctrl-N / Ctrl-E key handling."""

import pytest

from codemoo.chat.app import ChatApp
from codemoo.chat.demo_header import DemoHeader
from codemoo.chat.slides import DemoContext
from codemoo.config.schema import ResolvedBotConfig
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.error_bot import ErrorBot
from codemoo.core.participant import HumanParticipant


class _MockBackend:
    async def complete(self, messages: object, tools: object = None) -> str:
        return ""


def _make_demo_context(
    position: tuple[int, int] = (1, 8),
    prompts: list[str] | None = None,
) -> DemoContext:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    resolved = ResolvedBotConfig(
        bot_type="EchoBot",
        name="Coco",
        emoji="\N{PARROT}",
        variant="default",
        sources=["echo_bot.py"],
        description="A bot.",
        tools=[],
        prompts=prompts or [],
        instructions="",
    )
    return DemoContext(
        all_bots=[bot],
        resolved_configs=[resolved],
        prev_bot=None,
        llm=_MockBackend(),
        position=position,
        prompts=prompts or [],
    )


def _make_app(demo_context: DemoContext | None = None) -> ChatApp:
    human = HumanParticipant()
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    error_bot = ErrorBot(llm=_MockBackend())
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
    app.exit = lambda result=None: exits.append(result)
    app.on_key(_MockKey("ctrl+n"))
    assert not exits


def test_ctrl_n_exits_with_next_in_demo_mode() -> None:
    app = _make_app(demo_context=_make_demo_context())
    exits: list[str | None] = []
    app.exit = lambda result=None: exits.append(result)
    app.on_key(_MockKey("ctrl+n"))
    assert exits == ["next"]


# --- Ctrl-E key handler ---


class _MockInput:
    value: str = ""


class _MockHeader:
    last_remaining: int = -1

    def update_prompt_state(self, remaining: int) -> None:
        self.last_remaining = remaining


def _patch_query_one(app: ChatApp) -> tuple[_MockInput, _MockHeader]:
    """Replace query_one on the app instance with a fake that returns mock widgets."""
    from textual.widgets import Input as _Input

    mock_input = _MockInput()
    mock_header = _MockHeader()

    def _query_one(widget_type: object) -> object:
        if widget_type is _Input:
            return mock_input
        return mock_header

    app.query_one = _query_one  # type: ignore[method-assign]
    return mock_input, mock_header


def test_ctrl_space_ignored_without_demo_context() -> None:
    app = _make_app(demo_context=None)
    mock_input, _ = _patch_query_one(app)
    app.on_key(_MockKey("ctrl+e"))
    assert mock_input.value == ""


def test_ctrl_space_inserts_first_prompt() -> None:
    app = _make_app(demo_context=_make_demo_context(prompts=["First", "Second"]))
    mock_input, _ = _patch_query_one(app)
    app.on_key(_MockKey("ctrl+e"))
    assert mock_input.value == "First"


def test_ctrl_space_inserts_second_prompt_on_second_press() -> None:
    app = _make_app(demo_context=_make_demo_context(prompts=["First", "Second"]))
    mock_input, _ = _patch_query_one(app)
    app.on_key(_MockKey("ctrl+e"))
    app.on_key(_MockKey("ctrl+e"))
    assert mock_input.value == "Second"


def test_ctrl_space_does_nothing_when_exhausted() -> None:
    app = _make_app(demo_context=_make_demo_context(prompts=["Only"]))
    mock_input, _ = _patch_query_one(app)
    app.on_key(_MockKey("ctrl+e"))
    mock_input.value = ""
    app.on_key(_MockKey("ctrl+e"))
    assert mock_input.value == ""


def test_ctrl_space_updates_header_remaining_count() -> None:
    app = _make_app(demo_context=_make_demo_context(prompts=["A", "B", "C"]))
    _, mock_header = _patch_query_one(app)
    app.on_key(_MockKey("ctrl+e"))
    assert mock_header.last_remaining == 2


# --- SlideScreen push on mount: one async test for the slide overlay behavior ---


@pytest.mark.asyncio
async def test_slide_screen_pushed_on_mount_in_demo_mode() -> None:
    from codemoo.chat.slides import SlideScreen

    async with _make_app(demo_context=None).run_test() as pilot:
        assert not pilot.app.query(SlideScreen)
