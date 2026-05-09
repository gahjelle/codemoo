"""Tests for greeter.py."""

from greeter import greet, load_names


def test_greet() -> None:
    assert greet("Coco 🦜") == "Hello, Coco 🦜!"
    assert greet("Lore 📖") == "Hello, Lore 📖!"


def test_load_names() -> None:
    names = load_names("names.txt")
    assert len(names) == 11
    assert "Coco 🦜" in names
    assert "Lore 📖" in names
