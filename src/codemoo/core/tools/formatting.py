"""Formatting utilities for tool call display."""


def format_tool_call(
    name: str,
    arguments: dict[str, object],
    *,
    max_value_len: int | None = None,
) -> str:
    """Format a tool call as a function-call signature string.

    String values are quoted; non-strings use repr(). When max_value_len is
    set, each rendered value is truncated to that length with … (U+2026).
    Newlines in string values are replaced with spaces before truncation.
    """
    if not arguments:
        return f"{name}()"
    parts = []
    for k, v in arguments.items():
        v_str = f'"{v.replace(chr(10), " ")}"' if isinstance(v, str) else repr(v)
        if max_value_len is not None and len(v_str) > max_value_len:
            v_str = v_str[: max_value_len - 1] + "\N{HORIZONTAL ELLIPSIS}"
        parts.append(f"{k}={v_str}")
    return f"{name}({', '.join(parts)})"
