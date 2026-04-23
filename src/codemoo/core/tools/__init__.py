"""Reusable tool definitions: JSON schema and implementation paired together."""

import dataclasses
import subprocess
from collections.abc import Callable
from pathlib import Path

__all__ = ["ToolDef", "read_file", "reverse_string", "run_shell", "write_file"]


@dataclasses.dataclass
class ToolDef:
    """A tool: the JSON schema the LLM sees, and the Python callable to invoke."""

    schema: dict[str, object]
    fn: Callable[..., str]


#
# Read file
#
def _read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


read_file = ToolDef(
    schema={
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a file at the given path and return them as text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    fn=_read_file,
)


#
# Write file
#
def _write_file(path: str, content: str) -> str:
    num_bytes = Path(path).write_text(content, encoding="utf-8")
    return f"{num_bytes} bytes written"


write_file = ToolDef(
    schema={
        "type": "function",
        "function": {
            "name": "write_file",
            "description": ("Write the contents to a file at the given path."),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content that will be written to file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    fn=_write_file,
)


#
# Reverse string
#
def _reverse(text: str) -> str:
    return text[::-1]


reverse_string = ToolDef(
    schema={
        "type": "function",
        "function": {
            "name": "reverse_string",
            "description": "Reverse the characters in a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The string to reverse.",
                    }
                },
                "required": ["text"],
            },
        },
    },
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
    schema={
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": (
                "Execute a shell command and return its exit code, stdout, and stderr."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    fn=_run_shell,
)
