"""Shared utility for reading project context from file or SharePoint."""

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codemoo.core.bots.commentator_bot import CommentatorBot


@dataclasses.dataclass(frozen=True)
class ContextLoadEvent:
    """Emitted when a bot loads project context."""

    bot_name: str
    source: str  # "file", "sharepoint", or "drive"
    path: str  # "AGENTS.md", "sharepoint:TEAM.md", or "drive:TEAM.md"
    content: str  # Full content of the context file


@dataclasses.dataclass(frozen=True)
class MemoryLoadEvent:
    """Emitted when a bot loads its memory file."""

    bot_name: str
    source: str  # always "file"
    path: str  # path to the memory file
    content: str  # Full content of the memory file


async def read_project_context(
    context_source: dict[str, str] | None,
    bot_name: str,
    commentator: "CommentatorBot",
    session_folder: Path,
) -> str | None:
    """Read project context from file or SharePoint.

    Args:
        context_source: Config dict with 'type' and 'name' keys
            (e.g., {"type": "file", "name": "AGENTS.md"})
        bot_name: Name of the bot loading context
        commentator: CommentatorBot instance for emitting events
        session_folder: Root directory for file-based context lookup

    Returns:
        Context content if successful, None if not found or on error.

    """
    if not context_source:
        return None

    source_type = context_source.get("type", "file")
    source_name = context_source.get("name", "")

    if not source_name:
        return None

    content: str | None = None

    try:
        if source_type == "sharepoint":
            from codemoo.config import config  # noqa: PLC0415
            from codemoo.m365.tools.read import _read_sharepoint  # noqa: PLC0415

            site_path = f"{config.m365.sharepoint_host}:{config.m365.sharepoint_site}"
            content = _read_sharepoint(site_path, source_name)
        elif source_type == "drive":
            from codemoo.workspace.tools.read import _read_gdrive_by_name  # noqa: PLC0415,I001

            content = _read_gdrive_by_name(source_name)
        else:  # file
            context_file = session_folder / source_name
            if context_file.exists():
                content = context_file.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return None

    if content:
        path = (
            f"{source_type}:{source_name}"
            if source_type in {"sharepoint", "drive"}
            else source_name
        )
        await commentator.comment(
            ContextLoadEvent(
                bot_name=bot_name,
                source=source_type,
                path=path,
                content=content,
            )
        )

    return content


async def read_memory_file(
    memory_file_path: Path,
    bot_name: str,
    commentator: "CommentatorBot",
) -> str | None:
    """Read the bot's memory file if it exists and emit a MemoryLoadEvent.

    Returns the file contents on success, None if absent or on any error.
    """
    try:
        if not memory_file_path.exists():  # noqa: ASYNC240
            return None
        content = memory_file_path.read_text(encoding="utf-8")  # noqa: ASYNC240
    except Exception:  # noqa: BLE001
        return None

    if content:
        await commentator.comment(
            MemoryLoadEvent(
                bot_name=bot_name,
                source="file",
                path=str(memory_file_path),
                content=content,
            )
        )

    return content or None
