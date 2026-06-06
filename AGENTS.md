# AGENTS.md

Codemoo — an agentic loop application built with Python 3.14, used to demonstrate how coding agents like OpenCode and Claude Code work under the hood.

## Development Commands

This project uses `uv` for package management.

```bash
uv sync                                     # install dependencies
uv run codemoo                              # run the TUI as a coding assistant
uv run codemoo demo                         # run the TUI in demo mode
uv run demoo llm "query"                    # single LLM call with trace
uv run demoo tool "query"                   # one tool call + follow-up
uv run demoo agent "query"                  # agentic tool loop
uv run pytest                               # run tests
uv run ruff check . && uv run ruff format . # lint and format
uv run ty check .                           # type check (ty, not mypy)
```

## Code Style

- Type hints required on all functions
- Type checker is `ty` — use `# ty: ignore[<code>]` for suppression; never `# type: ignore[mypy-code]`
- Functional Core, Imperative Shell architecture
- Comments explain why, not what

## Detail Docs

- [Code style and linting](docs/agents/code-style.md)
- [Demo environment — intentional bugs, do not fix](docs/agents/demo-environment.md)
- [Bot configuration](docs/agents/bot-configuration.md)
- [Commentator configuration](docs/agents/commentator-configuration.md)
- [Context architecture](docs/agents/context-architecture.md)
- [Tools architecture](docs/agents/tools-architecture.md)
