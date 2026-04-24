"""Tests for codemoo.config."""

import pytest

from codemoo.config import language_instruction


def test_language_instruction_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEMOO_LANGUAGE", "Norwegian")
    assert language_instruction() == " Answer in Norwegian."


def test_language_instruction_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CODEMOO_LANGUAGE", raising=False)
    assert language_instruction() == " Answer in English."


def test_language_instruction_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEMOO_LANGUAGE", "")
    assert language_instruction() == " Answer in English."
