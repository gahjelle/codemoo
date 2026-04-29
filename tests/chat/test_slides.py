"""Tests for the demo slide overlay: AgendaColumn, _build_llm_prompt, SlideScreen."""

import pytest

from codemoo.chat.slides import (
    AgendaColumn,
    DemoContext,
    SlideContent,
    SlideScreen,
    _build_llm_prompt,
    _parse_numbered_list,
)
from codemoo.config.schema import ResolvedBotConfig
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
        LlmBot(name="Mono", emoji="\N{SPARKLES}", llm=_MockBackend()),
    ]


def _resolved(
    bot_type: str = "EchoBot",
    name: str = "Coco",
    sources: list[str] | None = None,
    description: str = "A bot.",
    tools: list[str] | None = None,
) -> ResolvedBotConfig:
    return ResolvedBotConfig(
        bot_type=bot_type,  # type: ignore[arg-type]
        name=name,
        emoji="\N{PARROT}",
        variant="default",
        sources=sources or ["echo_bot.py"],
        description=description,
        tools=tools or [],
        prompts=[],
        instructions="",
    )


def _make_context(position: tuple[int, int] = (1, 1)) -> DemoContext:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoContext(
        all_bots=[bot],
        resolved_configs=[_resolved()],
        prev_bot=None,
        llm=_MockBackend(),
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
        LlmBot(name="Mono", emoji="\N{SPARKLES}", llm=_MockBackend()),
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
    resolved = _resolved(bot_type="EchoBot", name="Coco", sources=["echo_bot.py"])
    prompt = _build_llm_prompt(resolved, previous=None)
    assert "Coco" in prompt
    assert "EchoBot" in prompt
    assert "echo_bot.py" in prompt


def test_build_llm_prompt_comparison_includes_both_bots() -> None:
    prev_resolved = _resolved(bot_type="EchoBot", name="Coco", sources=["echo_bot.py"])
    curr_resolved = _resolved(bot_type="LlmBot", name="Mono", sources=["llm_bot.py"])
    prompt = _build_llm_prompt(curr_resolved, previous=prev_resolved)
    assert "Coco" in prompt
    assert "Mono" in prompt
    assert "echo_bot.py" in prompt
    assert "llm_bot.py" in prompt


def test_build_llm_prompt_includes_tool_names_when_present() -> None:
    from codemoo.core.tools import reverse_string

    prev_resolved = _resolved(bot_type="EchoBot", name="Coco", sources=["echo_bot.py"])
    curr_resolved = _resolved(
        bot_type="ToolBot",
        name="Telo",
        sources=["tool_bot.py"],
        tools=[reverse_string.name],
    )
    prompt = _build_llm_prompt(curr_resolved, previous=prev_resolved)
    assert "reverse_string" in prompt


def test_build_llm_prompt_no_tools_line_when_no_tools() -> None:
    resolved = _resolved()
    prompt = _build_llm_prompt(resolved, previous=None)
    assert "tools:" not in prompt


# --- SlideContent: description label regression test ---


def test_slide_content_description_comes_from_resolved_config() -> None:
    """Regression: slides use resolved_configs[i].description, not a config lookup."""
    from textual.widgets import Label

    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    resolved = _resolved(description="M365 variant — not the code description")
    content = SlideContent(
        current_bot=bot,
        current_resolved=resolved,
        prev_bot=None,
        prev_resolved=None,
        llm=_MockBackend(),
    )
    description_labels = [
        w
        for w in content.compose()
        if isinstance(w, Label) and w.id == "slide-description"
    ]
    assert len(description_labels) == 1
    assert "M365 variant" in str(description_labels[0].content)


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


# --- _parse_numbered_list ---


def test_parse_numbered_list_extracts_items() -> None:
    text = "1. Hello\n2. World"
    assert _parse_numbered_list(text, 2) == ["Hello", "World"]


def test_parse_numbered_list_returns_none_on_count_mismatch() -> None:
    text = "1. Hello\n2. World"
    assert _parse_numbered_list(text, 3) is None


def test_parse_numbered_list_ignores_non_numbered_lines() -> None:
    text = "Here are the translations:\n1. Hei\n2. Verden\nDone."
    assert _parse_numbered_list(text, 2) == ["Hei", "Verden"]


# --- SlideScreen prompt translation ---


class _TranslatingBackend:
    """Backend that returns a numbered list translation."""

    def __init__(self, translations: list[str]) -> None:
        self._translations = translations
        self.call_count = 0

    async def complete(self, messages: object) -> str:
        self.call_count += 1
        return "\n".join(f"{i}. {t}" for i, t in enumerate(self._translations, start=1))

    async def complete_step(self, messages: object, tools: object) -> object:
        from codemoo.core.backend import TextResponse

        return TextResponse(text="")


def _make_context_with_prompts(
    prompts: list[str], backend: object | None = None
) -> DemoContext:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoContext(
        all_bots=[bot],
        resolved_configs=[_resolved()],
        prev_bot=None,
        llm=backend or _MockBackend(),
        position=(1, 1),
        prompts=list(prompts),
    )


@pytest.mark.asyncio
async def test_translate_prompts_replaces_prompts_on_success() -> None:
    backend = _TranslatingBackend(["Hei", "Verden"])
    ctx = _make_context_with_prompts(["Hello", "World"], backend)
    screen = SlideScreen(ctx)
    await screen._translate_prompts()
    assert ctx.prompts == ["Hei", "Verden"]


@pytest.mark.asyncio
async def test_translate_prompts_keeps_originals_on_count_mismatch() -> None:
    backend = _TranslatingBackend(["Hei"])  # returns 1 item, expected 2
    ctx = _make_context_with_prompts(["Hello", "World"], backend)
    screen = SlideScreen(ctx)
    await screen._translate_prompts()
    assert ctx.prompts == ["Hello", "World"]
