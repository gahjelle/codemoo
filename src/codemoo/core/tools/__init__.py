"""Reusable tool definitions: JSON schema and implementation paired together."""

import dataclasses
from collections.abc import Callable

__all__ = ["ToolDef", "reverse_string"]


@dataclasses.dataclass
class ToolDef:
    """A tool: the JSON schema the LLM sees, and the Python callable to invoke."""

    schema: dict[str, object]
    fn: Callable[..., str]


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
