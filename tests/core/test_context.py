"""Tests for the read_project_context function."""

from pathlib import Path
from unittest.mock import patch

import pytest

from codemoo.core.bots.commentator_bot import LoadEvent
from codemoo.core.context import read_project_context


class _MockCommentator:
    def __init__(self) -> None:
        self.events: list[object] = []

    async def comment(self, event: object) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_drive_context_source_returns_content() -> None:
    commentator = _MockCommentator()
    with patch(
        "codemoo.workspace.tools.read._read_gdrive_by_name", return_value="team content"
    ):
        result = await read_project_context(
            context_source={"type": "drive", "name": "TEAM.md"},
            bot_name="Lore",
            commentator=commentator,
            session_folder=Path.cwd(),
        )
    assert result == "team content"


@pytest.mark.asyncio
async def test_drive_context_source_emits_load_event() -> None:
    commentator = _MockCommentator()
    with patch(
        "codemoo.workspace.tools.read._read_gdrive_by_name", return_value="team content"
    ):
        await read_project_context(
            context_source={"type": "drive", "name": "TEAM.md"},
            bot_name="Lore",
            commentator=commentator,
            session_folder=Path.cwd(),
        )
    assert len(commentator.events) == 1
    event = commentator.events[0]
    assert isinstance(event, LoadEvent)
    assert event.kind == "context"
    assert event.source == "drive"
    assert event.path == "drive:TEAM.md"
    assert event.bot_name == "Lore"
    assert event.content == "team content"


@pytest.mark.asyncio
async def test_drive_context_source_file_not_found_returns_none() -> None:
    commentator = _MockCommentator()
    with patch("codemoo.workspace.tools.read._read_gdrive_by_name", return_value=None):
        result = await read_project_context(
            context_source={"type": "drive", "name": "TEAM.md"},
            bot_name="Lore",
            commentator=commentator,
            session_folder=Path.cwd(),
        )
    assert result is None
    assert commentator.events == []


@pytest.mark.asyncio
async def test_drive_context_source_exception_returns_none() -> None:
    commentator = _MockCommentator()
    with patch(
        "codemoo.workspace.tools.read._read_gdrive_by_name",
        side_effect=Exception("auth error"),
    ):
        result = await read_project_context(
            context_source={"type": "drive", "name": "TEAM.md"},
            bot_name="Lore",
            commentator=commentator,
            session_folder=Path.cwd(),
        )
    assert result is None
