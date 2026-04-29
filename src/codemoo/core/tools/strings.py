"""String operation tools."""

from codemoo.core.tools import ToolDef, ToolParam


def _reverse(text: str) -> str:
    return text[::-1]


reverse_string = ToolDef(
    name="reverse_string",
    description="Reverse the characters in a string.",
    parameters=[ToolParam(name="text", description="The string to reverse.")],
    fn=_reverse,
)
