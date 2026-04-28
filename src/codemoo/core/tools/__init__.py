"""Reusable tool definitions: structured schema and implementation paired together."""

import dataclasses
import subprocess
from collections.abc import Callable
from pathlib import Path

__all__ = [
    "TOOL_REGISTRY",
    "ToolDef",
    "ToolParam",
    "format_tool_call",
    "list_files",
    "read_file",
    "reverse_string",
    "run_shell",
    "write_file",
]

from codemoo.core.tools.formatting import format_tool_call


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


#
# Read file
#
def _read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


read_file = ToolDef(
    name="read_file",
    description=(
        "Read the contents of a file at the given path and return them as text."
    ),
    parameters=[ToolParam(name="path", description="The file path to read.")],
    fn=_read_file,
)


#
# Write file
#
def _write_file(path: str, content: str) -> str:
    num_bytes = Path(path).write_text(content, encoding="utf-8")
    return f"{num_bytes} bytes written"


write_file = ToolDef(
    name="write_file",
    description="Write the contents to a file at the given path.",
    parameters=[
        ToolParam(name="path", description="The file path to write."),
        ToolParam(
            name="content",
            description="The text content that will be written to file.",
        ),
    ],
    fn=_write_file,
    requires_approval=True,
)


#
# Reverse string
#
def _reverse(text: str) -> str:
    return text[::-1]


reverse_string = ToolDef(
    name="reverse_string",
    description="Reverse the characters in a string.",
    parameters=[ToolParam(name="text", description="The string to reverse.")],
    fn=_reverse,
)


#
# Run shell command
#
def _run_shell(command: str, _timeout: int = 30) -> str:
    try:
        result = subprocess.run(  # noqa: S602
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"[timeout after {_timeout}s] Command did not complete: {command}"
    parts = [f"exit code: {result.returncode}"]
    if result.stdout:
        parts.append(f"stdout:\n{result.stdout.rstrip()}")
    if result.stderr:
        parts.append(f"stderr:\n{result.stderr.rstrip()}")
    return "\n".join(parts)


run_shell = ToolDef(
    name="run_shell",
    description="Execute a shell command and return its exit code, stdout, and stderr.",
    parameters=[ToolParam(name="command", description="The shell command to run.")],
    fn=_run_shell,
    requires_approval=True,
)


#
# List files
#
def _list_files(path: str) -> str:
    p = Path(path)
    if not p.is_dir():
        return f"Error: {path!r} is not a valid directory"
    return "\n".join(entry.name for entry in sorted(p.iterdir()))


list_files = ToolDef(
    name="list_files",
    description="List the files and directories inside a directory path.",
    parameters=[ToolParam(name="path", description="The directory path to list.")],
    fn=_list_files,
)


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
