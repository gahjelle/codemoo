"""Demo slide overlay shown before each bot session in demo mode."""

import dataclasses
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Label, Markdown

from codemoo.chat.slides_data import BOT_DESCRIPTIONS, BOT_SOURCES
from codemoo.core.backend import LLMBackend, Message
from codemoo.core.participant import ChatParticipant

_BOTS_DIR = Path(__file__).parent.parent / "core" / "bots"


@dataclasses.dataclass
class DemoContext:
    """All demo-specific state passed from tui.py through ChatApp to SlideScreen."""

    all_bots: list[ChatParticipant]
    prev_bot: ChatParticipant | None
    backend: LLMBackend
    position: tuple[int, int]


def _read_source(filename: str) -> str:
    return (_BOTS_DIR / filename).read_text()


def _tool_names(bot: ChatParticipant) -> list[str]:
    tools = getattr(bot, "tools", None)
    if not tools:
        return []
    names = []
    for tool in tools:
        fn_block = tool.schema.get("function", {})
        name = fn_block.get("name", "")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def _bot_source_block(bot: ChatParticipant) -> str:
    bot_type = type(bot)
    files = BOT_SOURCES.get(bot_type, [f"{bot_type.__name__.lower()}.py"])
    return "\n".join(f"--- {f} ---\n{_read_source(f)}" for f in files)


def _build_llm_prompt(
    current_bot: ChatParticipant,
    prev_bot: ChatParticipant | None,
) -> str:
    """Build the LLM prompt for the slide's what's-new explanation."""
    curr_type = type(current_bot).__name__
    curr_source = _bot_source_block(current_bot)
    curr_tools = _tool_names(current_bot)
    curr_tools_line = f"\n{current_bot.name} tools: {curr_tools}" if curr_tools else ""

    if prev_bot is None:
        return (
            f"You're explaining a demo coding agent called {current_bot.name} "
            f"({curr_type}) to a live audience.\n\n"
            f"Here is its implementation:\n{curr_source}{curr_tools_line}\n\n"
            "Explain in 5-8 lines what this bot does and how it works. "
            "Be code-focused. Use Markdown — show the key line(s) of code in a "
            "fenced Python code block. Be concise — this must fit on a single screen."
        )

    prev_type = type(prev_bot).__name__
    prev_source = _bot_source_block(prev_bot)
    prev_tools = _tool_names(prev_bot)
    prev_tools_line = f"\n{prev_bot.name} tools: {prev_tools}" if prev_tools else ""

    return (
        f"You're explaining to a live audience what {current_bot.name} "
        f"({curr_type}) adds over {prev_bot.name} ({prev_type}).\n\n"
        f"{prev_bot.name} source:\n{prev_source}{prev_tools_line}\n\n"
        f"{current_bot.name} source:\n{curr_source}{curr_tools_line}\n\n"
        "Explain the single most important change in 5-8 lines. Be code-focused. "
        "Use Markdown — show the key code difference in a fenced Python code block. "
        "Don't explain helper functions in detail — focus on the concept. "
        "This must fit on a single screen."
    )


class AgendaColumn(Widget):
    """Thin left column listing the session bots with past/current/upcoming styling."""

    DEFAULT_CSS = """
    AgendaColumn {
        width: 22;
        height: 1fr;
    }
    """

    def __init__(self, all_bots: list[ChatParticipant], current_index: int) -> None:
        """Initialise with the full session bot list and the 0-based current index."""
        super().__init__()
        self._all_bots = all_bots
        self._current_index = current_index

    def compose(self) -> ComposeResult:
        """Yield one label per bot with the appropriate agenda CSS class."""
        for i, bot in enumerate(self._all_bots):
            if i < self._current_index:
                css_class = "agenda--past"
            elif i == self._current_index:
                css_class = "agenda--current"
            else:
                css_class = "agenda--upcoming"
            yield Label(f"{bot.emoji} {bot.name}", classes=css_class)


class SlideContent(Widget):
    """Main slide area: title, one-liner description, async LLM explanation."""

    DEFAULT_CSS = """
    SlideContent {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(
        self,
        current_bot: ChatParticipant,
        prev_bot: ChatParticipant | None,
        backend: LLMBackend,
    ) -> None:
        """Initialise with the current bot, optional predecessor, and backend."""
        super().__init__()
        self._current_bot = current_bot
        self._prev_bot = prev_bot
        self._backend = backend

    def compose(self) -> ComposeResult:
        """Yield the title, description, what's-new area, and dismiss button."""
        bot_type = type(self._current_bot).__name__
        description = BOT_DESCRIPTIONS.get(type(self._current_bot), "")
        yield Label(
            f"Meet {self._current_bot.name}, a {bot_type}",
            id="slide-title",
        )
        yield Label(description, id="slide-description")
        yield Label("What\N{APOSTROPHE}s new", id="slide-whats-new-header")
        yield Markdown("Generating\N{HORIZONTAL ELLIPSIS}", id="slide-whats-new")
        yield Button("OK", id="slide-ok", variant="primary")

    def on_mount(self) -> None:
        """Fire the async worker that loads the LLM explanation."""
        self.run_worker(self._load_explanation(), exclusive=True)

    async def _load_explanation(self) -> None:
        prompt = _build_llm_prompt(self._current_bot, self._prev_bot)
        text = await self._backend.complete([Message(role="user", content=prompt)])
        await self.query_one("#slide-whats-new", Markdown).update(text)


class SlideScreen(ModalScreen[None]):
    """Full-screen modal overlay introducing a bot before its chat session."""

    def __init__(self, context: DemoContext) -> None:
        """Initialise with the full demo context for this session."""
        super().__init__()
        self._demo_ctx = context  # avoid collision with MessagePump._context

    def compose(self) -> ComposeResult:
        """Yield the two-column slide layout."""
        current_index = self._demo_ctx.position[0] - 1
        current_bot = self._demo_ctx.all_bots[current_index]
        with Vertical(id="slide-outer"):
            yield Horizontal(
                AgendaColumn(self._demo_ctx.all_bots, current_index),
                SlideContent(
                    current_bot, self._demo_ctx.prev_bot, self._demo_ctx.backend
                ),
                id="slide-layout",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss the slide when OK is clicked."""
        if event.button.id == "slide-ok":
            self.dismiss()

    def on_key(self, event: Key) -> None:
        """Dismiss the slide on Enter or Escape so the presenter isn't blocked."""
        if event.key in ("enter", "escape"):
            event.stop()
            self.dismiss()
