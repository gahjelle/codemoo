"""Tests for greeter.py."""

from greeter import greet, load_names


def test_greet() -> None:
    assert greet("Coco 🦜") == "Hello, Coco 🦜!"
    assert greet("Cato 🔒") == "Hello, Cato 🔒!"


def test_load_names() -> None:
    names = load_names("names.txt")
    assert len(names) == 9
    assert "Coco 🦜" in names
    assert "Cato 🔒" in names
