"""Tests for TUI helper functions."""

import pytest

from codemoo.frontends.tui import _default_script_for_mode


def test_default_script_for_code_mode() -> None:
    # "default" is the first code-mode script declared in codemoo.toml
    assert _default_script_for_mode("code") == "default"


def test_default_script_for_business_mode() -> None:
    # "m365" is the first business-mode script declared in codemoo.toml
    assert _default_script_for_mode("business") == "m365"


def test_default_script_raises_for_missing_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import codemoo.frontends.tui as tui_module

    monkeypatch.setattr(tui_module, "config", type("_Cfg", (), {"scripts": {}})())
    with pytest.raises(StopIteration):
        _default_script_for_mode("code")
