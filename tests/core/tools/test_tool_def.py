from typing import cast
from unittest.mock import MagicMock

from codemoo.core.bots import run_init_hooks
from codemoo.core.tools import ToolDef, ToolParam
from codemoo.core.tools.files import read_file, write_file
from codemoo.core.tools.shell import run_shell
from codemoo.core.tools.strings import reverse_string
from codemoo.llm.mistral import _MistralBackend
from codemoo.m365.tools import M365_TOOL_REGISTRY


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


def test_tool_def_init_defaults_to_none() -> None:
    def my_fn(x: str) -> str:
        return x

    t = ToolDef(name="t", description="", parameters=[], fn=my_fn)
    assert t.init is None


def test_code_tools_have_no_init_hook() -> None:
    for tool in [read_file, write_file, run_shell, reverse_string]:
        assert tool.init is None


def test_m365_tools_have_init_hook() -> None:
    for tool in M365_TOOL_REGISTRY.values():
        assert tool.init is not None


def test_m365_tools_share_same_init_hook() -> None:
    tools = list(M365_TOOL_REGISTRY.values())
    assert all(t.init is tools[0].init for t in tools)


def test_run_init_hooks_calls_hook_once_per_unique_fn() -> None:
    call_log: list[str] = []

    def hook_a() -> None:
        call_log.append("a")

    def hook_b() -> None:
        call_log.append("b")

    def noop(x: str) -> str:
        return x

    tools = [
        ToolDef(name="t1", description="", parameters=[], fn=noop, init=hook_a),
        ToolDef(name="t2", description="", parameters=[], fn=noop, init=hook_a),
        ToolDef(name="t3", description="", parameters=[], fn=noop, init=hook_b),
    ]
    run_init_hooks(tools)
    assert call_log == ["a", "b"]


def test_run_init_hooks_skips_none_init() -> None:
    called: list[bool] = []

    def noop(x: str) -> str:
        return x

    tools = [ToolDef(name="t", description="", parameters=[], fn=noop, init=None)]
    run_init_hooks(tools)
    assert called == []


def test_reverse_string_schema_top_level_fields() -> None:
    backend = _MistralBackend(client=MagicMock(), model="test")
    schema = backend._tool_schema(reverse_string)
    assert schema["type"] == "function"
    fn_block = schema["function"]
    assert isinstance(fn_block, dict)
    assert fn_block["name"] == "reverse_string"
    assert "description" in fn_block
    params = fn_block["parameters"]
    assert isinstance(params, dict)
    assert "text" in cast("dict[str, object]", params["properties"])
    assert params["required"] == ["text"]
