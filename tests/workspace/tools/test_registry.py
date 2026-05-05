"""Tests for WORKSPACE_TOOL_REGISTRY structure."""

from codemoo.workspace.tools import WORKSPACE_TOOL_REGISTRY


def test_workspace_registry_contains_gmail_tools() -> None:
    assert "list_gmail" in WORKSPACE_TOOL_REGISTRY
    assert "read_gmail" in WORKSPACE_TOOL_REGISTRY
    assert "send_gmail" in WORKSPACE_TOOL_REGISTRY


def test_workspace_registry_contains_gcal_tools() -> None:
    assert "list_gcal" in WORKSPACE_TOOL_REGISTRY
    assert "create_gcal_event" in WORKSPACE_TOOL_REGISTRY


def test_workspace_registry_contains_chat_tool() -> None:
    assert "post_chat_message" in WORKSPACE_TOOL_REGISTRY


def test_workspace_registry_keys_match_tool_names() -> None:
    for key, tool in WORKSPACE_TOOL_REGISTRY.items():
        assert key == tool.name


def test_workspace_write_tools_require_approval() -> None:
    for name in ("send_gmail", "create_gcal_event", "post_chat_message"):
        assert WORKSPACE_TOOL_REGISTRY[name].requires_approval


def test_workspace_read_tools_do_not_require_approval() -> None:
    for name in ("list_gmail", "read_gmail", "list_gcal"):
        assert not WORKSPACE_TOOL_REGISTRY[name].requires_approval


def test_all_workspace_tools_have_init_hook() -> None:
    for tool in WORKSPACE_TOOL_REGISTRY.values():
        assert tool.init is not None
