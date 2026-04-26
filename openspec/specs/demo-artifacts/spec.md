# Spec: demo-artifacts

## Purpose

Defines the `demo/` folder — a self-contained greeter project used as the subject of the Acts 3–4 demo prompts. The folder provides stable, purpose-built artifacts that demo bots can read, run, diagnose, fix, and commit.

## Requirements

### Requirement: demo/names.txt lists the nine bot names with their emojis
The file `demo/names.txt` SHALL contain exactly nine non-empty lines. Each line SHALL be in the format `<BotName> <emoji>`, listing the nine implemented bots in demo progression order:
Coco 🦜, Mono ✨, Iris 🧿, Sona 🎭, Telo 🔧, Rune 📁, Ash 🐚, Loom 🌀, Cato 🔒.
Every line SHALL contain at least one non-ASCII character (the emoji), making the file unreadable with ASCII encoding.

#### Scenario: File contains exactly nine non-empty lines
- **WHEN** `demo/names.txt` is read
- **THEN** it SHALL contain exactly nine non-empty lines

#### Scenario: Every line contains an emoji
- **WHEN** each line of `demo/names.txt` is inspected
- **THEN** every line SHALL contain at least one character outside the ASCII range

### Requirement: demo/greeter.py reads names.txt with ascii encoding and crashes on emoji
`demo/greeter.py` SHALL be a short standalone Python script containing:
- A `load_names(path: str) -> list[str]` function that opens the given path with `encoding="ascii"` (the intentional bug)
- A `greet(name: str) -> str` function returning `f"Hello, {name}!"`
- A `main()` function that calls `load_names("names.txt")` and prints each greeting
- An `if __name__ == "__main__": main()` guard

The script SHALL have full type annotations and a module docstring. The encoding bug causes a `UnicodeDecodeError` when run, because `names.txt` contains emoji characters.

#### Scenario: Running greeter.py raises UnicodeDecodeError
- **WHEN** `python greeter.py` is executed with `demo/` as the working directory
- **THEN** the process SHALL exit with a non-zero return code and stderr SHALL contain `UnicodeDecodeError`

#### Scenario: Fixing encoding to utf-8 produces correct output
- **WHEN** `load_names` is changed to use `encoding="utf-8"` and `python greeter.py` is executed
- **THEN** stdout SHALL contain `Hello, Coco 🦜!` through `Hello, Cato 🔒!`, nine lines in total

### Requirement: demo/test_greeter.py imports and tests greeter functions directly
`demo/test_greeter.py` SHALL be a pytest test file that imports `load_names` and `greet` from `greeter` and tests them directly. Tests SHALL fail when the encoding bug is present (a `UnicodeDecodeError` from `load_names`) and pass after it is fixed.

#### Scenario: Tests fail before the encoding bug is fixed
- **WHEN** `uv run pytest test_greeter.py` is run from `demo/` with the original `greeter.py`
- **THEN** at least one test SHALL fail with `UnicodeDecodeError`

#### Scenario: Tests pass after the encoding bug is fixed
- **WHEN** `load_names` in `greeter.py` uses `encoding="utf-8"` and `uv run pytest test_greeter.py` is run from `demo/`
- **THEN** all tests SHALL pass

#### Scenario: Tests verify greeting format and names list
- **WHEN** the fixed `greeter.py` is imported
- **THEN** the test SHALL assert `greet("Coco 🦜") == "Hello, Coco 🦜!"` and that `load_names("names.txt")` returns a list containing `"Coco 🦜"` and `"Cato 🔒"`

### Requirement: demo/README.md describes the greeter project with one intentional inaccuracy
`demo/README.md` SHALL read as a genuine project README — purpose, usage instructions, and file descriptions. It SHALL claim that the script "sorts names alphabetically before greeting them." The actual `greeter.py` code SHALL NOT sort. This discrepancy is intentional: it makes the Rune prompt "Compare README.md and greeter.py" reveal a real difference rather than confirming everything is consistent.

#### Scenario: README claims names are sorted alphabetically
- **WHEN** `demo/README.md` is read
- **THEN** it SHALL contain text asserting that names are sorted (or presented in alphabetical order)

#### Scenario: greeter.py does not sort names
- **WHEN** `greeter.py` source code is inspected
- **THEN** it SHALL NOT contain a `sort` or `sorted` call
