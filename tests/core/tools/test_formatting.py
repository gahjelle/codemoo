from codemoo.core.tools import format_tool_call


def test_no_args_produces_empty_parens() -> None:
    assert format_tool_call("foo", {}) == "foo()"


def test_string_value_is_quoted() -> None:
    result = format_tool_call("run_shell", {"command": "ls -la"})
    assert result == 'run_shell(command="ls -la")'


def test_non_string_value_uses_repr_without_quotes() -> None:
    assert format_tool_call("f", {"n": 42}) == "f(n=42)"


def test_no_truncation_when_max_value_len_is_none() -> None:
    long = "x" * 200
    result = format_tool_call("f", {"v": long})
    assert long in result
    assert "\N{HORIZONTAL ELLIPSIS}" not in result


def test_long_value_truncated_at_max_value_len() -> None:
    result = format_tool_call("f", {"v": "x" * 100}, max_value_len=10)
    # value_part includes the trailing ")" from the call signature
    value_part = result.split("v=")[1].rstrip(")")
    assert len(value_part) == 10
    assert value_part.endswith("\N{HORIZONTAL ELLIPSIS}")


def test_short_value_not_truncated() -> None:
    result = format_tool_call("f", {"v": "hello"}, max_value_len=40)
    assert "\N{HORIZONTAL ELLIPSIS}" not in result
    assert '"hello"' in result


def test_newlines_replaced_with_spaces() -> None:
    result = format_tool_call("write_file", {"content": "line1\nline2"})
    assert "\n" not in result
    assert "line1 line2" in result


def test_newlines_replaced_before_truncation() -> None:
    result = format_tool_call("f", {"v": "ab\ncd"}, max_value_len=6)
    assert "\n" not in result


def test_multiple_args_formatted_correctly() -> None:
    result = format_tool_call("write_file", {"path": "f.py", "content": "hello"})
    assert result == 'write_file(path="f.py", content="hello")'


def test_truncation_ends_with_ellipsis_not_raw_char() -> None:
    result = format_tool_call("f", {"v": "abcdefghij"}, max_value_len=6)
    assert "\N{HORIZONTAL ELLIPSIS}" in result
    assert "..." not in result
