"""Shared utility for reading project context from file or SharePoint."""

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codemoo.core.bots.commentator_bot import CommentatorBot


@dataclasses.dataclass(frozen=True)
class ContextLoadEvent:
    """Emitted when a bot loads project context."""

    bot_name: str
    source: str  # "file" or "sharepoint"
    path: str  # "AGENTS.md" or "sharepoint:TEAM.md"
    content: str  # Full content of the context file


async def read_project_context(
    context_source: dict[str, str] | None,
    bot_name: str,
    commentator: "CommentatorBot",
) -> str | None:
    """Read project context from file or SharePoint.

    Args:
        context_source: Config dict with 'type' and 'name' keys
            (e.g., {"type": "file", "name": "AGENTS.md"})
        bot_name: Name of the bot loading context
        commentator: CommentatorBot instance for emitting events

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
        else:  # file
            from pathlib import Path  # noqa: PLC0415

            context_file = Path(source_name)
            if context_file.exists():  # noqa: ASYNC240
                content = context_file.read_text(encoding="utf-8")  # noqa: ASYNC240
    except Exception:  # noqa: BLE001
        return None

    if content:
        path = (
            f"{source_type}:{source_name}"
            if source_type == "sharepoint"
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
