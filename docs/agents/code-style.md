# Code Style

## Linting and Formatting

Ruff is used for both linting and formatting, with all rules enabled. Only three rules are disabled: COM812, D203, D213.

```bash
uv run ruff check .
uv run ruff format .
```

## Type Checking

The type checker is `ty` (not mypy). Do not use `mypy` or `# type: ignore[mypy-code]`.

For suppression, use:

```python
# ty: ignore[<code>]
```

Tests have a blanket `ty` override in `pyproject.toml` for Textual mock patterns — no per-line ignores needed in test files.

## Architecture

Functional Core, Imperative Shell: pure functions in the core, side effects at the boundary.

## Comments

Comments explain *why*, not *what*. Well-named identifiers carry the what.
