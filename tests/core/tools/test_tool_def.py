from typing import cast

from codemoo.core.tools import ToolDef, ToolParam
from codemoo.core.tools.files import read_file, write_file
from codemoo.core.tools.shell import run_shell
from codemoo.core.tools.strings import reverse_string
from codemoo.llm.mistral import _tool_schema


def test_tool_def_exposes_name_and_fn() -> None:
    def my_fn(x: str) -> str:
        return x

    t = ToolDef(
        name="my_tool",
        description="A test tool.",
        parameters=[ToolParam(name="x", description="Input.")],
        fn=my_fn,
    )
    assert t.name == "my_tool"
    assert t.fn is my_fn


def test_tool_def_requires_approval_defaults_to_false() -> None:
    def my_fn(x: str) -> str:
        return x

    t = ToolDef(
        name="my_tool",
        description="A test tool.",
        parameters=[],
        fn=my_fn,
    )
    assert t.requires_approval is False


def test_run_shell_requires_approval() -> None:
    assert run_shell.requires_approval is True


def test_write_file_requires_approval() -> None:
    assert write_file.requires_approval is True


def test_read_file_does_not_require_approval() -> None:
    assert read_file.requires_approval is False


def test_reverse_string_does_not_require_approval() -> None:
    assert reverse_string.requires_approval is False


def test_reverse_string_ascii() -> None:
    assert reverse_string.fn(text="hello") == "olleh"


def test_reverse_string_empty() -> None:
    assert reverse_string.fn(text="") == ""


def test_reverse_string_unicode() -> None:
    assert reverse_string.fn(text="abc") == "cba"
    assert reverse_string.fn(text="élève") == "evèlé"


def test_reverse_string_schema_top_level_fields() -> None:
    schema = _tool_schema(reverse_string)
    assert schema["type"] == "function"
    fn_block = schema["function"]
    assert isinstance(fn_block, dict)
    assert fn_block["name"] == "reverse_string"
    assert "description" in fn_block
    params = fn_block["parameters"]
    assert isinstance(params, dict)
    assert "text" in cast("dict[str, object]", params["properties"])
    assert params["required"] == ["text"]
