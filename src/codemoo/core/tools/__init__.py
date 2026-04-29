"""Reusable tool definitions: structured schema and implementation paired together."""

import dataclasses
from collections.abc import Callable


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


@dataclasses.dataclass
class ToolParam:
    """Description of a single tool parameter."""

    name: str
    description: str
    type: str = "string"
    required: bool = True


@dataclasses.dataclass
class ToolDef:
    """A tool: structured metadata the LLM sees, and the Python callable to invoke."""

    name: str
    description: str
    parameters: list[ToolParam]
    fn: Callable[..., str]
    requires_approval: bool = False


from codemoo.core.tools.files import list_files, read_file, write_file  # noqa: E402
from codemoo.core.tools.graph_read import (  # noqa: E402
    list_calendar,
    list_email,
    list_sharepoint,
    read_email,
    read_sharepoint,
)
from codemoo.core.tools.graph_write import (  # noqa: E402
    create_calendar_event,
    post_teams_message,
    send_email,
    write_sharepoint,
)
from codemoo.core.tools.shell import run_shell  # noqa: E402
from codemoo.core.tools.strings import reverse_string  # noqa: E402

__all__ = [
    "TOOL_REGISTRY",
    "ToolDef",
    "ToolParam",
    "format_tool_call",
]

TOOL_REGISTRY: dict[str, ToolDef] = {
    # Code tools
    "read_file": read_file,
    "write_file": write_file,
    "reverse_string": reverse_string,
    "run_shell": run_shell,
    "list_files": list_files,
    # M365 read tools
    "list_sharepoint": list_sharepoint,
    "read_sharepoint": read_sharepoint,
    "list_email": list_email,
    "read_email": read_email,
    "list_calendar": list_calendar,
    # M365 action tools
    "send_email": send_email,
    "create_calendar_event": create_calendar_event,
    "post_teams_message": post_teams_message,
    "write_sharepoint": write_sharepoint,
}
