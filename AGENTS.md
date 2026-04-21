# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project

Codaroo — an agentic loop application built with Python 3.14. Currently in early development. The project was earlier called Gaia (Geir Arne's Agentic Loop), and you may find that name in legacy documentation.

## Development Commands

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Run the CLI entry point
uv run codaroo

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
uv run ty check
```

## Code Style

- Ruff for linting/formatting with all rules enabled; only COM812, D203, D213 are disabled
- Type hints required on all functions
- Functional Core, Imperative Shell architecture
- Comments explain why, not what

## Textual Widget CSS

Widget CSS follows a structural/visual split:

- `DEFAULT_CSS` — properties the widget cannot function without (e.g. `height: auto`, `layout`, fractional widths). These travel with the widget class.
- External `.tcss` file — visual/thematic properties only (colors, borders, spacing).
