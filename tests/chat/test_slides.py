"""Tests for the demo slide overlay: AgendaColumn, _build_llm_prompt, SlideScreen."""

from codemoo.chat.slides import (
    AgendaColumn,
    DemoContext,
    SlideScreen,
    _build_llm_prompt,
)
from codemoo.core.backend import TextResponse, ToolUse
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.llm_bot import LlmBot


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return "Generated explanation"

    async def complete_step(
        self, messages: object, tools: object
    ) -> TextResponse | ToolUse:
        return TextResponse(text="")


def _make_bots() -> list[EchoBot | LlmBot]:
    return [
        EchoBot(name="Coco", emoji="\N{PARROT}"),
        LlmBot(name="Mono", emoji="\N{SPARKLES}", backend=_MockBackend()),
    ]


def _make_context(position: tuple[int, int] = (1, 1)) -> DemoContext:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoContext(
        all_bots=[bot],
        prev_bot=None,
        backend=_MockBackend(),
        position=position,
    )


# --- AgendaColumn: synchronous unit tests, no Textual app needed ---


def test_agenda_past_bot_has_past_class() -> None:
    bots = _make_bots()
    column = AgendaColumn(bots, current_index=1)
    labels = list(column.compose())
    assert "agenda--past" in labels[0].classes


def test_agenda_current_bot_has_current_class() -> None:
    bots = _make_bots()
    column = AgendaColumn(bots, current_index=0)
    labels = list(column.compose())
    assert "agenda--current" in labels[0].classes


def test_agenda_upcoming_bot_has_upcoming_class() -> None:
    bots = _make_bots()
    column = AgendaColumn(bots, current_index=0)
    labels = list(column.compose())
    assert "agenda--upcoming" in labels[1].classes


def test_agenda_all_three_states_with_three_bots() -> None:
    bots = [
        EchoBot(name="Coco", emoji="\N{PARROT}"),
        LlmBot(name="Mono", emoji="\N{SPARKLES}", backend=_MockBackend()),
        EchoBot(name="Other", emoji="\N{PARROT}"),
    ]
    column = AgendaColumn(bots, current_index=1)
    labels = list(column.compose())
    assert "agenda--past" in labels[0].classes
    assert "agenda--current" in labels[1].classes
    assert "agenda--upcoming" in labels[2].classes


def test_agenda_produces_one_label_per_bot() -> None:
    bots = _make_bots()
    column = AgendaColumn(bots, current_index=0)
    labels = list(column.compose())
    assert len(labels) == 2


# --- _build_llm_prompt: synchronous unit tests ---


def test_build_llm_prompt_first_bot_no_comparison() -> None:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    prompt = _build_llm_prompt(bot, prev_bot=None)
    assert "Coco" in prompt
    assert "EchoBot" in prompt
    assert "echo_bot.py" in prompt


def test_build_llm_prompt_comparison_includes_both_bots() -> None:
    prev = EchoBot(name="Coco", emoji="\N{PARROT}")
    curr = LlmBot(name="Mono", emoji="\N{SPARKLES}", backend=_MockBackend())
    prompt = _build_llm_prompt(curr, prev_bot=prev)
    assert "Coco" in prompt
    assert "Mono" in prompt
    assert "echo_bot.py" in prompt
    assert "llm_bot.py" in prompt


def test_build_llm_prompt_includes_tool_names_when_present() -> None:
    from codemoo.core.bots.tool_bot import ToolBot
    from codemoo.core.tools import reverse_string

    prev = EchoBot(name="Coco", emoji="\N{PARROT}")
    curr = ToolBot(
        name="Telo",
        emoji="\N{WRENCH}",
        backend=_MockBackend(),
        human_name="You",
        tools=[reverse_string],
        instructions="",
    )
    prompt = _build_llm_prompt(curr, prev_bot=prev)
    assert "reverse_string" in prompt


def test_build_llm_prompt_no_tools_line_when_no_tools() -> None:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    prompt = _build_llm_prompt(bot, prev_bot=None)
    assert "tools:" not in prompt


# --- SlideScreen: dismiss handler unit tests ---
# Test handler logic directly without a running Textual app.


class _MockKey:
    """Minimal stand-in for textual.events.Key."""

    def __init__(self, key: str) -> None:
        self.key = key
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True


class _MockButton:
    """Minimal stand-in for textual.widgets.Button."""

    def __init__(self, widget_id: str) -> None:
        self.id = widget_id


class _MockButtonPressed:
    """Minimal stand-in for textual.widgets.Button.Pressed."""

    def __init__(self, button_id: str) -> None:
        self.button = _MockButton(button_id)


def _screen_with_mock_dismiss() -> tuple[SlideScreen, list[None]]:
    screen = SlideScreen(_make_context())
    calls: list[None] = []
    screen.dismiss = lambda result=None: calls.append(result)
    return screen, calls


def test_slide_screen_enter_key_dismisses() -> None:
    screen, calls = _screen_with_mock_dismiss()
    event = _MockKey("enter")
    screen.on_key(event)
    assert calls
    assert event._stopped


def test_slide_screen_escape_key_dismisses() -> None:
    screen, calls = _screen_with_mock_dismiss()
    event = _MockKey("escape")
    screen.on_key(event)
    assert calls
    assert event._stopped


def test_slide_screen_other_key_does_not_dismiss() -> None:
    screen, calls = _screen_with_mock_dismiss()
    event = _MockKey("ctrl+n")
    screen.on_key(event)
    assert not calls


def test_slide_screen_ok_button_dismisses() -> None:
    screen, calls = _screen_with_mock_dismiss()
    event = _MockButtonPressed("slide-ok")
    screen.on_button_pressed(event)
    assert calls


def test_slide_screen_other_button_does_not_dismiss() -> None:
    screen, calls = _screen_with_mock_dismiss()
    event = _MockButtonPressed("some-other-button")
    screen.on_button_pressed(event)
    assert not calls
