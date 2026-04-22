from typing import cast

from codemoo.core.tools import ToolDef, reverse_string


def test_tool_def_exposes_schema_and_fn() -> None:
    def my_fn(x: str) -> str:
        return x

    t = ToolDef(schema={"type": "function"}, fn=my_fn)
    assert t.schema == {"type": "function"}
    assert t.fn is my_fn


def test_reverse_string_ascii() -> None:
    assert reverse_string.fn(text="hello") == "olleh"


def test_reverse_string_empty() -> None:
    assert reverse_string.fn(text="") == ""


def test_reverse_string_unicode() -> None:
    assert reverse_string.fn(text="abc") == "cba"
    assert reverse_string.fn(text="élève") == "evèlé"


def test_reverse_string_schema_top_level_fields() -> None:
    schema = reverse_string.schema
    assert schema["type"] == "function"
    fn_block = cast("dict[str, object]", schema["function"])
    assert fn_block["name"] == "reverse_string"
    assert "description" in fn_block
    params = cast("dict[str, object]", fn_block["parameters"])
    assert "text" in cast("dict[str, object]", params["properties"])
    assert params["required"] == ["text"]
