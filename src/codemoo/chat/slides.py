"""Demo slide overlay shown before each bot session in demo mode."""

import dataclasses
import re
from collections.abc import Sequence

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Label, Markdown

from codemoo.config import config
from codemoo.config.schema import ResolvedBotConfig
from codemoo.core.backend import LLMBackend, Message
from codemoo.core.participant import ChatParticipant


@dataclasses.dataclass
class DemoContext:
    """All demo-specific state passed from tui.py through ChatApp to SlideScreen."""

    all_bots: list[ChatParticipant]
    resolved_configs: list[ResolvedBotConfig]
    prev_bot: ChatParticipant | None
    llm: LLMBackend
    position: tuple[int, int]
    prompts: list[str] = dataclasses.field(default_factory=list)
    cached_explanation: str | None = None


def _parse_numbered_list(text: str, expected: int) -> list[str] | None:
    """Extract items from a numbered list response; return None on count mismatch."""
    items = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^\d+\.", line.strip())
    ]
    return items if len(items) == expected else None


def _read_source(filename: str) -> str:
    return (config.paths.bots_dir / filename).read_text()


def _bot_source_block(resolved: ResolvedBotConfig) -> str:
    return "\n".join(f"--- {f} ---\n{_read_source(f)}" for f in resolved.sources)


def _build_llm_prompt(
    current: ResolvedBotConfig,
    previous: ResolvedBotConfig | None,
) -> str:
    """Build the LLM prompt for the slide's what's-new explanation."""
    curr_source = _bot_source_block(current)
    curr_tools_line = (
        f"\n{current.name} tools: {current.tools}" if current.tools else ""
    )
    curr_instructions_line = (
        f"\n{current.name} instructions:\n{current.instructions}"
        if current.instructions
        else ""
    )

    if previous is None:
        return (
            f"You're explaining a demo coding agent called {current.name} "
            f"({current.bot_type}) to a live audience.\n\n"
            f"Here is its implementation:\n{curr_source}{curr_tools_line}"
            f"{curr_instructions_line}\n\n"
            "Explain in 5-8 lines what this bot does and how it works. "
            "Be code-focused. Use Markdown — show the key line(s) of code in a "
            "fenced Python code block. Be concise — this must fit on a single screen. "
            f"Answer in {config.language}."
        )

    prev_source = _bot_source_block(previous)
    prev_tools_line = (
        f"\n{previous.name} tools: {previous.tools}" if previous.tools else ""
    )
    prev_instructions_line = (
        f"\n{previous.name} instructions:\n{previous.instructions}"
        if previous.instructions
        else ""
    )

    return (
        f"You're explaining to a live audience what {current.name} "
        f"({current.bot_type}) adds over {previous.name} ({previous.bot_type}).\n\n"
        f"{previous.name} source:\n{prev_source}{prev_tools_line}"
        f"{prev_instructions_line}\n\n"
        f"{current.name} source:\n{curr_source}{curr_tools_line}"
        f"{curr_instructions_line}\n\n"
        "Explain the single most important change in 5-8 lines. Be code-focused. "
        "Use Markdown — show the key code difference in a fenced Python code block. "
        "Don't explain helper functions in detail — focus on the concept. "
        f"This must fit on a single screen. Answer in {config.language}."
    )


class AgendaColumn(Widget):
    """Thin left column listing the session bots with past/current/upcoming styling."""

    DEFAULT_CSS = """
    AgendaColumn {
        width: 22;
        height: 1fr;
    }
    """

    def __init__(self, all_bots: Sequence[ChatParticipant], current_index: int) -> None:
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

    def __init__(self, demo_ctx: DemoContext) -> None:
        """Initialise with the full demo context for this session."""
        super().__init__()
        self._demo_ctx = demo_ctx

    def _current_index(self) -> int:
        return self._demo_ctx.position[0] - 1

    def compose(self) -> ComposeResult:
        """Yield the title, description, what's-new area, and dismiss button."""
        resolved = self._demo_ctx.resolved_configs[self._current_index()]
        yield Label(
            f"Meet {resolved.name}, the {resolved.bot_type}",
            id="slide-title",
        )
        yield Label(resolved.description, id="slide-description")
        yield Markdown("Generating\N{HORIZONTAL ELLIPSIS}", id="slide-whats-new")
        yield Button("OK", id="slide-ok", variant="primary")

    def on_mount(self) -> None:
        """Fire the async worker that loads the LLM explanation."""
        self.run_worker(self._load_explanation(), exclusive=True)

    async def _load_explanation(self) -> None:
        if self._demo_ctx.cached_explanation is not None:
            await self.query_one("#slide-whats-new", Markdown).update(
                self._demo_ctx.cached_explanation
            )
            return
        idx = self._current_index()
        current_resolved = self._demo_ctx.resolved_configs[idx]
        prev_resolved = self._demo_ctx.resolved_configs[idx - 1] if idx > 0 else None
        prompt = _build_llm_prompt(current_resolved, prev_resolved)
        text = await self._demo_ctx.llm.complete([Message(role="user", content=prompt)])
        self._demo_ctx.cached_explanation = text
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
        with Vertical(id="slide-outer"):
            yield Horizontal(
                AgendaColumn(self._demo_ctx.all_bots, current_index),
                SlideContent(self._demo_ctx),
                id="slide-layout",
            )

    def on_mount(self) -> None:
        """Launch prompt translation in the background while the slide is visible."""
        if config.language != "English" and self._demo_ctx.prompts:
            self.run_worker(self._translate_prompts(), exclusive=False)

    async def _translate_prompts(self) -> None:
        numbered = "\n".join(
            f"{i}. {p}" for i, p in enumerate(self._demo_ctx.prompts, start=1)
        )
        prompt = (
            f"Translate the following numbered prompts to {config.language}. "
            "Return them as a numbered list in the same format, with no extra text.\n\n"
            f"{numbered}"
        )
        response = await self._demo_ctx.llm.complete(
            [Message(role="user", content=prompt)]
        )
        translated = _parse_numbered_list(response, len(self._demo_ctx.prompts))
        if translated is not None:
            self._demo_ctx.prompts = translated

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dismiss the slide when OK is clicked."""
        if event.button.id == "slide-ok":
            self.dismiss()

    def on_key(self, event: Key) -> None:
        """Dismiss the slide on Enter or Escape so the presenter isn't blocked."""
        if event.key in ("enter", "escape"):
            event.stop()
            self.dismiss()
