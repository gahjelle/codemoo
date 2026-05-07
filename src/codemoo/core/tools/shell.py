"""Shell operation tools."""

import shlex
import subprocess
from collections.abc import Callable
from pathlib import Path

from codemoo.core.tools import ToolDef, ToolParam


def make_shell_validator(session_folder: Path) -> Callable[..., str | None]:
    """Return a validator that blocks shell commands with paths outside session_folder."""  # noqa: E501
    resolved_root = session_folder.resolve()

    def _validate(command: str, **_: object) -> str | None:
        try:
            tokens = shlex.split(command)
        except ValueError:
            return (
                f"Blocked: the command could not be parsed."
                f" Only shell commands using paths within the session folder"
                f" '{resolved_root}' are permitted."
            )
        for token in tokens:
            # Split --flag=value form; check the value part
            _pre, _sep, flag_value = token.partition("=")
            candidate = flag_value or token
            if candidate.startswith("..") or (
                candidate.startswith("/") and not candidate.startswith("./")
            ):
                return (
                    f"Blocked: the command contains '{candidate}', which references a"
                    f" path outside the session folder '{resolved_root}'."
                    " Use paths relative to the session folder instead."
                )
        return None

    return _validate


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
