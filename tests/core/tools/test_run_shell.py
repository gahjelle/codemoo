from typing import cast

from codemoo.core.tools import run_shell


def test_successful_command_returns_stdout() -> None:
    result = run_shell.fn(command="echo hello")
    assert "hello" in result
    assert "exit code: 0" in result


def test_failing_command_returns_nonzero_exit_code_without_raising() -> None:
    result = run_shell.fn(command="exit 1")
    assert "exit code: 1" in result


def test_stderr_included_in_output() -> None:
    result = run_shell.fn(command="echo error >&2; exit 2")
    assert "error" in result
    assert "exit code: 2" in result


def test_timeout_returns_message_not_exception() -> None:
    result = run_shell.fn(command="sleep 10", _timeout=1)
    assert "timeout" in result.lower()


def test_schema_top_level_fields() -> None:
    from codemoo.llm.mistral import _tool_schema

    schema = _tool_schema(run_shell)
    assert schema["type"] == "function"
    fn_block = cast("dict[str, object]", schema["function"])
    assert fn_block["name"] == "run_shell"
    assert "description" in fn_block
    params = cast("dict[str, object]", fn_block["parameters"])
    assert "command" in cast("dict[str, object]", params["properties"])
    assert params["required"] == ["command"]
