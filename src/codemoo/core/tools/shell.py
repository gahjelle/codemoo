"""Shell operation tools."""

import subprocess

from codemoo.core.tools import ToolDef, ToolParam


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
