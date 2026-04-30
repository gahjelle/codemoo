from pathlib import Path
from typing import cast

import pytest

from codemoo.core.tools.files import read_file


def test_read_file_returns_contents(tmp_path: Path) -> None:
    f = tmp_path / "hello.txt"
    f.write_text("hello world")
    assert read_file.fn(path=str(f)) == "hello world"


def test_read_file_nonexistent_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_file.fn(path=str(tmp_path / "no_such_file.txt"))


def test_read_file_schema_top_level_fields() -> None:
    from unittest.mock import MagicMock

    from codemoo.llm.mistral import _MistralBackend

    backend = _MistralBackend(client=MagicMock(), model="test")
    schema = backend._tool_schema(read_file)
    assert schema["type"] == "function"
    fn_block = cast("dict[str, object]", schema["function"])
    assert fn_block["name"] == "read_file"
    assert "description" in fn_block
    params = cast("dict[str, object]", fn_block["parameters"])
    assert "path" in cast("dict[str, object]", params["properties"])
    assert params["required"] == ["path"]
