"""Tests for Google Drive workspace tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codemoo.workspace.tools import WORKSPACE_TOOL_REGISTRY
from codemoo.workspace.tools.read import (
    _list_gdrive,
    _read_gdrive,
    _read_gdrive_by_name,
    _read_gdrive_content,
)
from codemoo.workspace.tools.write import _write_gdrive

_GDOC_MIME = "application/vnd.google-apps.document"
_HEADERS = {"Authorization": "Bearer test-token"}


def _mock_client(*responses: MagicMock) -> MagicMock:
    """Return a mock AsyncClient context manager that yields sequential responses."""
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    if len(responses) == 1:
        client.get = AsyncMock(return_value=responses[0])
        client.post = AsyncMock(return_value=responses[0])
        client.patch = AsyncMock(return_value=responses[0])
        client.put = AsyncMock(return_value=responses[0])
    else:
        client.get = AsyncMock(side_effect=list(responses))
        client.post = AsyncMock(side_effect=list(responses))
        client.patch = AsyncMock(side_effect=list(responses))
        client.put = AsyncMock(side_effect=list(responses))
    return client


# list_gdrive


@pytest.mark.asyncio
async def test_list_gdrive_returns_name_and_id_lines() -> None:
    mock_resp = MagicMock()
    mock_resp.is_error = False
    mock_resp.json.return_value = {
        "files": [
            {"name": "TEAM.md", "id": "abc123"},
            {"name": "notes.txt", "id": "def456"},
        ]
    }
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(mock_resp),
        ),
    ):
        result = await _list_gdrive()
    assert "TEAM.md  |  abc123" in result
    assert "notes.txt  |  def456" in result


@pytest.mark.asyncio
async def test_list_gdrive_empty_folder() -> None:
    mock_resp = MagicMock()
    mock_resp.is_error = False
    mock_resp.json.return_value = {"files": []}
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(mock_resp),
        ),
    ):
        result = await _list_gdrive()
    assert result == "No files found"


@pytest.mark.asyncio
async def test_list_gdrive_api_error() -> None:
    mock_resp = MagicMock()
    mock_resp.is_error = True
    mock_resp.status_code = 403
    mock_resp.text = "Forbidden"
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(mock_resp),
        ),
    ):
        result = await _list_gdrive()
    assert result == "Error 403: Forbidden"


# _read_gdrive_content


@pytest.mark.asyncio
async def test_read_gdrive_content_exports_google_doc() -> None:
    mock_resp = MagicMock()
    mock_resp.is_error = False
    mock_resp.text = "Doc content"
    client = MagicMock()
    client.get = AsyncMock(return_value=mock_resp)
    with patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS):
        result = await _read_gdrive_content(client, "file-id", _GDOC_MIME)
    assert result == "Doc content"


@pytest.mark.asyncio
async def test_read_gdrive_content_downloads_text_file() -> None:
    mock_resp = MagicMock()
    mock_resp.is_error = False
    mock_resp.text = "# Hello"
    client = MagicMock()
    client.get = AsyncMock(return_value=mock_resp)
    with patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS):
        result = await _read_gdrive_content(client, "file-id", "text/plain")
    assert result == "# Hello"


@pytest.mark.asyncio
async def test_read_gdrive_content_unsupported_mime_type() -> None:
    client = MagicMock()
    result = await _read_gdrive_content(client, "file-id", "application/pdf")
    assert "Unsupported file type" in result
    assert "application/pdf" in result


# _read_gdrive


@pytest.mark.asyncio
async def test_read_gdrive_fetches_metadata_then_content() -> None:
    meta_resp = MagicMock()
    meta_resp.is_error = False
    meta_resp.json.return_value = {
        "id": "abc",
        "name": "notes.txt",
        "mimeType": "text/plain",
    }

    content_resp = MagicMock()
    content_resp.is_error = False
    content_resp.text = "file content"

    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(meta_resp, content_resp),
        ),
    ):
        result = await _read_gdrive("abc")
    assert result == "file content"


@pytest.mark.asyncio
async def test_read_gdrive_metadata_error() -> None:
    meta_resp = MagicMock()
    meta_resp.is_error = True
    meta_resp.status_code = 404
    meta_resp.text = "Not Found"
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(meta_resp),
        ),
    ):
        result = await _read_gdrive("no-such-id")
    assert "Error 404" in result


# _read_gdrive_by_name


@pytest.mark.asyncio
async def test_read_gdrive_by_name_returns_content_when_found() -> None:
    search_resp = MagicMock()
    search_resp.is_error = False
    search_resp.json.return_value = {"files": [{"id": "abc", "mimeType": "text/plain"}]}

    content_resp = MagicMock()
    content_resp.is_error = False
    content_resp.text = "team context"

    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(search_resp, content_resp),
        ),
    ):
        result = await _read_gdrive_by_name("TEAM.md")
    assert result == "team context"


@pytest.mark.asyncio
async def test_read_gdrive_by_name_returns_none_when_not_found() -> None:
    search_resp = MagicMock()
    search_resp.is_error = False
    search_resp.json.return_value = {"files": []}
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(search_resp),
        ),
    ):
        result = await _read_gdrive_by_name("TEAM.md")
    assert result is None


@pytest.mark.asyncio
async def test_read_gdrive_by_name_returns_none_on_api_error() -> None:
    search_resp = MagicMock()
    search_resp.is_error = True
    with (
        patch("codemoo.workspace.tools.read._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.read.httpx.AsyncClient",
            return_value=_mock_client(search_resp),
        ),
    ):
        result = await _read_gdrive_by_name("TEAM.md")
    assert result is None


# _write_gdrive


@pytest.mark.asyncio
async def test_write_gdrive_creates_new_file() -> None:
    search_resp = MagicMock()
    search_resp.is_error = False
    search_resp.json.return_value = {"files": []}

    create_resp = MagicMock()
    create_resp.is_error = False
    create_resp.json.return_value = {"id": "new-id"}

    client = _mock_client(search_resp)
    client.post = AsyncMock(return_value=create_resp)
    with (
        patch("codemoo.workspace.tools.write._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.write.httpx.AsyncClient",
            return_value=client,
        ),
    ):
        result = await _write_gdrive("TEAM.md", "content")
    assert result == "Created TEAM.md (new-id)"


@pytest.mark.asyncio
async def test_write_gdrive_updates_existing_file() -> None:
    search_resp = MagicMock()
    search_resp.is_error = False
    search_resp.json.return_value = {"files": [{"id": "existing-id"}]}

    patch_resp = MagicMock()
    patch_resp.is_error = False
    patch_resp.json.return_value = {"id": "existing-id"}

    client = _mock_client(search_resp)
    client.patch = AsyncMock(return_value=patch_resp)
    with (
        patch("codemoo.workspace.tools.write._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.write.httpx.AsyncClient",
            return_value=client,
        ),
    ):
        result = await _write_gdrive("TEAM.md", "updated content")
    assert result == "Updated TEAM.md (existing-id)"


@pytest.mark.asyncio
async def test_write_gdrive_search_error() -> None:
    search_resp = MagicMock()
    search_resp.is_error = True
    search_resp.status_code = 500
    search_resp.text = "Internal Error"
    with (
        patch("codemoo.workspace.tools.write._get_headers", return_value=_HEADERS),
        patch(
            "codemoo.workspace.tools.write.httpx.AsyncClient",
            return_value=_mock_client(search_resp),
        ),
    ):
        result = await _write_gdrive("TEAM.md", "content")
    assert "Error 500" in result


# Registry


def test_gdrive_tools_in_registry() -> None:
    assert "list_gdrive" in WORKSPACE_TOOL_REGISTRY
    assert "read_gdrive" in WORKSPACE_TOOL_REGISTRY
    assert "write_gdrive" in WORKSPACE_TOOL_REGISTRY


def test_write_gdrive_requires_approval() -> None:
    assert WORKSPACE_TOOL_REGISTRY["write_gdrive"].requires_approval


def test_read_gdrive_tools_do_not_require_approval() -> None:
    assert not WORKSPACE_TOOL_REGISTRY["list_gdrive"].requires_approval
    assert not WORKSPACE_TOOL_REGISTRY["read_gdrive"].requires_approval


def test_all_gdrive_tools_have_init_hook() -> None:
    for name in ("list_gdrive", "read_gdrive", "write_gdrive"):
        assert WORKSPACE_TOOL_REGISTRY[name].init is not None
