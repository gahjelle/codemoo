"""Shell operation tools."""

import asyncio
import shlex
from collections.abc import Callable
from pathlib import Path

from codemoo.core.tools import ToolDef, ToolParam


def make_shell_validator(session_folder: Path) -> Callable[..., str | None]:
    """Return a validator blocking shell commands with paths outside session_folder."""
    resolved_root = session_folder.resolve()

    def _validate(command: str, **_: object) -> str | None:
        try:
            tokens = shlex.split(command)
        except ValueError:
            return (
                f"Error: the command could not be parsed."
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
                    f"Error: the command contains '{candidate}', which references a"
                    f" path outside the session folder '{resolved_root}'."
                    " Use paths relative to the session folder instead."
                )
        return None

    return _validate


async def _run_shell(command: str, _timeout: int = 30) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=_timeout
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            return (
                f"Error: timeout after {_timeout}s. Command did not complete: {command}"
            )
    except OSError as err:
        return f"Error: {err}"

    stdout = stdout_bytes.decode(errors="replace")
    stderr = stderr_bytes.decode(errors="replace")

    if proc.returncode:
        return "\n".join(
            [
                f"Error: {stderr.rstrip()}",
                f"exit code: {proc.returncode}",
                f"stdout:\n{stdout.rstrip()}" if stdout.strip() else "",
            ]
        )

    return "\n".join(
        [
            f"stdout:\n{stdout.rstrip()}",
            f"stderr:\n{stderr.rstrip()}" if stderr.strip() else "",
            f"exit code: {proc.returncode}",
        ]
    )


run_shell = ToolDef(
    name="run_shell",
    description="Execute a shell command and return its exit code, stdout, and stderr.",
    parameters=[ToolParam(name="command", description="The shell command to run.")],
    fn=_run_shell,
    requires_approval=True,
)
