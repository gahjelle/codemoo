# AGENTS.md

This file provides guidance for agents working with the Greeter demo project.

## Project

A simple Python greeter application that reads names from a file and outputs
personalized greetings. This is used to demonstrate how the Codemoo code
assistant can be used in development.

## Development Commands

```bash
# Run the main script
uv run greeter.py

# Run tests
uv run pytest test_greeter.py
```

## Known Issues (Intentional for Demo)

- **greeter.py**: Uses `encoding="ascii"` which causes `UnicodeDecodeError` with
  non-ASCII characters in names.txt. This is the bug the demo asks the agent to
  diagnose and fix.

- **README.md**: Claims the script "sorts names alphabetically" but the code does
  not sort. This discrepancy is intentional for the demo.

Do not fix these issues unless explicitly asked.
