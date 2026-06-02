"""Tests for greeter.py."""

from greeter import greet, load_names


def test_greet() -> None:
    assert greet("Coco 🦜") == "Hello, Coco 🦜!"
    assert greet("Drop 🧹") == "Hello, Drop 🧹!"


def test_load_names() -> None:
    names = load_names("names.txt")
    assert len(names) == 13
    assert "Coco 🦜" in names
    assert "Drop 🧹" in names
