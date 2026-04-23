# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project

Codemoo — an agentic loop application built with Python 3.14. The project will be used to demonstrate how coding agents like OpenCode and Claude Code work under the hood.

The project was earlier called Gaia (Geir Arne's AI Assistant) and Coderoo, and you may find those names in legacy documentation.

## Development Commands

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Run the CLI entry point
uv run codemoo

# Run Python directly
uv run python

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run ty check .
```

## Code Style

- Ruff for linting/formatting with all rules enabled; only COM812, D203, D213 are disabled
- Type hints required on all functions
- Functional Core, Imperative Shell architecture
- Comments explain why, not what
- Type checker is `ty` (not mypy) — use `# ty: ignore[<code>]` if suppression is ever needed; never `# type: ignore[mypy-code]`. Tests have a blanket override in `pyproject.toml` for Textual mock patterns, so no per-line ignores are needed there.

## Textual Widget CSS

Widget CSS follows a structural/visual split:

- `DEFAULT_CSS` — properties the widget cannot function without (e.g. `height: auto`, `layout`, fractional widths). These travel with the widget class.
- External `.tcss` file — visual/thematic properties only (colors, borders, spacing).
