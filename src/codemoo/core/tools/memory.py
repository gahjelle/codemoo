"""Memory persistence tool for MemoryBot."""

import functools
from pathlib import Path

from codemoo.core.tools import ToolDef, ToolParam


def _save_memory(content: str, *, path: Path) -> str:
    """Write content to the memory file, replacing any previous contents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Memory saved to {path}"


def make_memory_tool(path: Path) -> ToolDef:
    """Return a save_memory ToolDef with the memory file path pre-baked."""
    return ToolDef(
        name="save_memory",
        description=(
            "Save your memory about this user and project, replacing any previous"
            " memory. Call this when you observe facts, preferences, or patterns"
            " worth keeping across sessions. Write the memory file in English."
        ),
        parameters=[
            ToolParam(
                name="content",
                description=(
                    "The complete new contents of the memory file (free-form Markdown)."
                ),
            )
        ],
        fn=functools.partial(_save_memory, path=path),
    )
