"""Reusable tool definitions: structured schema and implementation paired together."""

import dataclasses
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codemoo.core.bots.commentator_bot import CommentatorBot


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
    init: Callable[[], None] | None = None
    validate: Callable[..., str | None] | None = None


from codemoo.core.tools.files import list_files, read_file, write_file  # noqa: E402
from codemoo.core.tools.shell import run_shell  # noqa: E402
from codemoo.core.tools.strings import reverse_string  # noqa: E402
from codemoo.core.tools.system import get_datetime  # noqa: E402

__all__ = [
    "TOOL_REGISTRY",
    "ToolDef",
    "ToolParam",
    "dispatch_tool",
    "format_tool_call",
]


async def dispatch_tool(
    tool: ToolDef,
    arguments: dict[str, object],
    bot_name: str,
    commentator: "CommentatorBot | None",
) -> str:
    """Run validate (if present), then fn. Emits ValidationBlockEvent on block."""
    if tool.validate is not None:
        error = tool.validate(**arguments)
        if error is not None:
            if commentator is not None:
                from codemoo.core.bots.commentator_bot import ValidationBlockEvent  # noqa: PLC0415, I001

                await commentator.comment(
                    ValidationBlockEvent(
                        bot_name=bot_name,
                        tool_name=tool.name,
                        arguments=arguments,
                        reason=error,
                    )
                )
            return error
    return tool.fn(**arguments)


TOOL_REGISTRY: dict[str, ToolDef] = {
    "read_file": read_file,
    "write_file": write_file,
    "reverse_string": reverse_string,
    "run_shell": run_shell,
    "list_files": list_files,
    "get_datetime": get_datetime,
}
