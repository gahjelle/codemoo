"""Tests for estimate_tokens() in token_counter.py."""

import tiktoken

from codemoo.core.backend import Message
from codemoo.core.token_counter import estimate_tokens


def test_empty_list_returns_zero() -> None:
    assert estimate_tokens([]) == 0


def test_counts_content_tokens() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    msg = Message(role="user", content="hello world")
    assert estimate_tokens([msg]) == len(enc.encode("hello world"))


def test_counts_tool_calls_json_tokens() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    tool_json = '{"name": "read_file", "arguments": {"path": "foo.py"}}'
    msg = Message(role="assistant", content="", tool_calls_json=tool_json)
    expected = len(enc.encode("")) + len(enc.encode(tool_json))
    assert estimate_tokens([msg]) == expected


def test_content_and_tool_calls_json_summed() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    content = "Calling a tool"
    tool_json = '{"name": "run_shell"}'
    msg = Message(role="assistant", content=content, tool_calls_json=tool_json)
    expected = len(enc.encode(content)) + len(enc.encode(tool_json))
    assert estimate_tokens([msg]) == expected


def test_none_tool_calls_json_adds_no_tokens() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    msg = Message(role="user", content="hello", tool_calls_json=None)
    assert estimate_tokens([msg]) == len(enc.encode("hello"))


def test_sums_across_multiple_messages() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    msgs = [
        Message(role="user", content="hello"),
        Message(role="assistant", content="world"),
    ]
    expected = len(enc.encode("hello")) + len(enc.encode("world"))
    assert estimate_tokens(msgs) == expected
