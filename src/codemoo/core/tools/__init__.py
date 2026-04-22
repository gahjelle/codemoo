"""Reusable tool definitions: JSON schema and implementation paired together."""

import dataclasses
from collections.abc import Callable
from pathlib import Path

__all__ = ["ToolDef", "read_file", "reverse_string"]


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
