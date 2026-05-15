"""Animated cowsay splash screen shown at startup before heavy imports load."""

import asyncio
import random

from rich.text import Text
from textual.app import App, ComposeResult
from textual.geometry import Size
from textual.widget import Widget

# ---------------------------------------------------------------------------
# Code snippet — each line is a list of (text, rich_style | None) segments
# ---------------------------------------------------------------------------

_CODE_LINES: list[list[tuple[str, str | None]]] = [
    [("while", "bold #7aa2f7"), (" True:", None)],
    [("    thought = ", None), ("llm", "#9ece6a"), (".think()", None)],
    [("    ", None), ("if", "bold #7aa2f7"), (" thought:", None)],
    [("        ", None), ("moo", "#9ece6a"), ("()", None)],
]

_LINE_LENGTHS: list[int] = [sum(len(t) for t, _ in segs) for segs in _CODE_LINES]

# Cumulative start position of each line in the flat character stream
_LINE_STARTS: list[int] = [sum(_LINE_LENGTHS[:i]) for i in range(len(_LINE_LENGTHS))]

_TOTAL_CHARS: int = sum(_LINE_LENGTHS)

# ---------------------------------------------------------------------------
# Box geometry
# ---------------------------------------------------------------------------

_BOX_CONTENT_WIDTH = 34  # characters inside "│ " … " │"
_BOX_HEADER = "┌─ agent_loop.py " + "─" * 20 + "┐"  # 38 chars total
_BOX_FOOTER = "└" + "─" * 36 + "┘"  # 38 chars total

# Tail animation — two frames
_TAILS = ["\\/\\", "/\\/"]

# Head animation — probability that a blink is followed by a tongue flick
_TONGUE_PROBABILITY = 0.3

# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------


def _build_line_text(line_idx: int, n_chars: int) -> Text:
    """Return styled Rich Text for the first *n_chars* of the given code line."""
    result = Text()
    remaining = n_chars
    for seg_text, style in _CODE_LINES[line_idx]:
        if remaining <= 0:
            break
        visible = seg_text[:remaining]
        remaining -= len(seg_text)
        if style:
            result.append(visible, style=style)
        else:
            result.append(visible)
    return result


def _active_line(pos: int) -> int:
    """Return the index of the line currently being typed into."""
    return next(
        (i for i in range(len(_LINE_STARTS) - 1, -1, -1) if pos >= _LINE_STARTS[i]),
        0,
    )


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

_RENDER_HEIGHT = 18  # total lines produced by render()


class CowWidget(Widget):
    """Renders the full animated cowsay splash from four independent state variables."""

    DEFAULT_CSS = """
    CowWidget {
        width: 43;
        height: 18;
        overflow: hidden hidden;
    }
    """

    def __init__(self) -> None:
        """Initialise with default animation state."""
        super().__init__()
        self._code_pos: int = 0
        self._tail_frame: int = 0
        self._cursor_visible: bool = True
        self._head_state: str = "open"  # "open" | "blink" | "tongue"

    # ── State mutators (each calls refresh) ─────────────────────────────────

    def advance_code(self) -> None:
        """Advance the typewriter by one character."""
        if self._code_pos < _TOTAL_CHARS:
            self._code_pos += 1
            self.refresh()

    def toggle_cursor(self) -> None:
        """Toggle the blinking cursor on/off."""
        self._cursor_visible = not self._cursor_visible
        self.refresh()

    def toggle_tail(self) -> None:
        """Toggle the tail wiggle between its two frames."""
        self._tail_frame ^= 1
        self.refresh()

    def set_head_state(self, state: str) -> None:
        """Set the cow head animation state ('open', 'blink', or 'tongue')."""
        self._head_state = state
        self.refresh()

    # ── Layout hint ──────────────────────────────────────────────────────────

    def get_content_height(
        self,
        container: Size,  # noqa: ARG002
        viewport: Size,  # noqa: ARG002
        width: int,  # noqa: ARG002
    ) -> int:
        """Return the fixed render height."""
        return _RENDER_HEIGHT

    # ── Render ───────────────────────────────────────────────────────────────

    def render(self) -> Text:  # type: ignore[override]
        """Build and return the full splash art as a Rich Text object."""
        pos = self._code_pos
        tail = _TAILS[self._tail_frame]
        eyes = "--" if self._head_state == "blink" else "oo"
        show_tongue = self._head_state == "tongue"
        cursor = "█" if self._cursor_visible else " "
        active = _active_line(pos)
        typing_done = pos >= _TOTAL_CHARS

        out = Text()

        # ── Terminal code window ─────────────────────────────────────────────
        out.append("   ")
        out.append(_BOX_HEADER, style="dim")
        out.append("\n")

        for line_idx in range(4):
            n = max(0, min(pos - _LINE_STARTS[line_idx], _LINE_LENGTHS[line_idx]))
            line_text = _build_line_text(line_idx, n)
            is_active = (line_idx == active) and not typing_done

            out.append("   ")
            out.append("│ ", style="dim")
            out.append_text(line_text)
            if is_active:
                out.append(cursor, style="#9ece6a")
                padding = _BOX_CONTENT_WIDTH - n - 1
            else:
                padding = _BOX_CONTENT_WIDTH - n
            if padding > 0:
                out.append(" " * padding)
            out.append(" │", style="dim")
            out.append("\n")

        out.append("   ")
        out.append(_BOX_FOOTER, style="dim")
        out.append("\n")

        # ── Thought-bubble dots ──────────────────────────────────────────────
        out.append("        ·\n", style="dim")
        out.append("       ·\n", style="dim")
        out.append("      ·\n", style="dim")

        # ── Cow ──────────────────────────────────────────────────────────────
        out.append("   ^__^\n", style="bright_white")
        out.append(f"   ({eyes})\\_______\n", style="bright_white")
        out.append("   (__)\\       )", style="bright_white")
        out.append(tail + "\n", style="bright_white")

        # Tongue line is always present to prevent layout shift
        if show_tongue:
            out.append("     U", style="#f7768e")
        else:
            out.append("      ")

        out.append(" ||----w |\n", style="bright_white")
        out.append("       ||     ||\n", style="bright_white")
        out.append("\n")

        # ── Title ────────────────────────────────────────────────────────────
        out.append("      C O D E M O O\n", style="bold #7dcfff")
        out.append("    coding agents, step by step\n", style="dim italic")

        return out


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


class SplashApp(App[None]):
    """Shows the animated splash while heavy imports load in a background thread."""

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def __init__(self) -> None:
        """Initialise with default animation state."""
        super().__init__()
        self._cow: CowWidget

    def compose(self) -> ComposeResult:
        """Yield the single cow widget."""
        self._cow = CowWidget()
        yield self._cow

    def on_mount(self) -> None:
        """Start animation timers and kick off the background import worker."""
        self.set_interval(0.04, self._tick_typewriter)
        self.set_interval(0.5, self._tick_cursor)
        self.set_interval(0.6, self._tick_tail)
        self._schedule_head_tick()
        self.run_worker(self._load, thread=True)

    # ── Timer callbacks ──────────────────────────────────────────────────────

    def _tick_typewriter(self) -> None:
        self._cow.advance_code()

    def _tick_cursor(self) -> None:
        self._cow.toggle_cursor()

    def _tick_tail(self) -> None:
        self._cow.toggle_tail()

    def _schedule_head_tick(self) -> None:
        delay = random.uniform(0.5, 1.5)  # noqa: S311
        self.set_timer(delay, self._do_head_animation)

    async def _do_head_animation(self) -> None:
        show_tongue = random.random() < _TONGUE_PROBABILITY  # noqa: S311
        self._cow.set_head_state("blink")
        await asyncio.sleep(0.15)
        if show_tongue:
            self._cow.set_head_state("tongue")
            await asyncio.sleep(0.3)
        self._cow.set_head_state("open")
        self._schedule_head_tick()

    # ── Background worker ────────────────────────────────────────────────────

    def _load(self) -> None:
        import codemoo.frontends.tui  # noqa: PLC0415, F401 — triggers all heavy imports

        self.call_from_thread(self.exit, None)
