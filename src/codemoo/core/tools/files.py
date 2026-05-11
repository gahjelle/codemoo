"""File operation tools."""

from collections.abc import Callable
from pathlib import Path

from codemoo.core.tools import ToolDef, ToolParam


def make_file_validator(session_folder: Path) -> Callable[..., str | None]:
    """Return a validator that blocks any path outside session_folder."""
    resolved_root = session_folder.resolve()

    def _validate(path: str, **_: object) -> str | None:
        resolved = (resolved_root / path).resolve()
        if not resolved.is_relative_to(resolved_root):
            return (
                f"Blocked: '{path}' resolves to '{resolved}', which is outside the"
                f" session folder '{resolved_root}'."
                " Only paths within the session folder are permitted."
            )
        return None

    return _validate


def _read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as err:
        return f"Error: {err}"


read_file = ToolDef(
    name="read_file",
    description=(
        "Read the contents of a file at the given path and return them as text."
    ),
    parameters=[ToolParam(name="path", description="The file path to read.")],
    fn=_read_file,
)


def _write_file(path: str, content: str) -> str:
    try:
        num_bytes = Path(path).write_text(content, encoding="utf-8")
    except OSError as err:
        return f"Error: {err}"
    else:
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
