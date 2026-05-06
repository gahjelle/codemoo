"""Tests for config loading and pre-Pydantic resolution logic."""

import pytest

from codemoo.config import _resolve_file_refs


def _data(tool_lists: dict, tools: list) -> dict:
    return {
        "tool_lists": tool_lists,
        "bots": {"MyBot": {"variants": {"v": {"description": "x", "tools": tools}}}},
    }


def test_at_reference_expands_to_named_list() -> None:
    data = _data(
        tool_lists={"code_read": ["reverse_string", "read_file", "list_files"]},
        tools=["@code_read"],
    )
    _resolve_file_refs(data)
    assert data["bots"]["MyBot"]["variants"]["v"]["tools"] == [
        "reverse_string",
        "read_file",
        "list_files",
    ]


def test_at_reference_mixed_with_plain_tools_expands_in_place() -> None:
    data = _data(
        tool_lists={"code_read": ["reverse_string", "read_file"]},
        tools=["@code_read", "run_shell"],
    )
    _resolve_file_refs(data)
    assert data["bots"]["MyBot"]["variants"]["v"]["tools"] == [
        "reverse_string",
        "read_file",
        "run_shell",
    ]


def test_unknown_at_reference_raises_key_error_with_helpful_message() -> None:
    data = _data(
        tool_lists={"code_read": ["reverse_string"], "code_write": ["run_shell"]},
        tools=["@nonexistent"],
    )
    with pytest.raises(KeyError, match="nonexistent"):
        _resolve_file_refs(data)


def test_unknown_at_reference_error_message_lists_available() -> None:
    data = _data(
        tool_lists={"alpha": ["tool_a"], "beta": ["tool_b"]},
        tools=["@missing"],
    )
    with pytest.raises(KeyError) as exc_info:
        _resolve_file_refs(data)
    msg = str(exc_info.value)
    assert "missing" in msg
    assert "alpha" in msg
    assert "beta" in msg


def test_plain_tools_without_at_prefix_are_unchanged() -> None:
    data = _data(
        tool_lists={},
        tools=["reverse_string", "read_file"],
    )
    _resolve_file_refs(data)
    assert data["bots"]["MyBot"]["variants"]["v"]["tools"] == [
        "reverse_string",
        "read_file",
    ]


def test_tool_lists_is_consumed_from_data() -> None:
    data = _data(
        tool_lists={"code_read": ["reverse_string"]},
        tools=["@code_read"],
    )
    _resolve_file_refs(data)
    assert "tool_lists" not in data
