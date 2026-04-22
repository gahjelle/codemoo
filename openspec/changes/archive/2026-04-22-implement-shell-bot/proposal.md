## Why

ToolBot and FileBot demonstrated the tool-call pattern in isolation; ShellBot is the natural next step — showing that the same mechanism can give the LLM the ability to *run code*, not just read data. This is pedagogically the moment the demo transitions from "it can look at things" to "it can do things in the world," which is a pivotal point in Act 3 of the demo arc.

## What Changes

- Add a `run_shell` tool to `codemoo/core/tools/__init__.py` that executes a shell command via `subprocess` and returns its output.
- Introduce a `GeneralToolBot` base class that consolidates the shared `on_message` logic currently duplicated across `ToolBot` and `FileBot`.
- Refactor `ToolBot` and `FileBot` to inherit from `GeneralToolBot` (no change in external behaviour).
- Add `ShellBot`, inheriting from `GeneralToolBot`, wired to the `run_shell` tool.
- Register `ShellBot` (name **Ash**, emoji 🐚) in the main bot list in `codemoo/__init__.py`.

## Capabilities

### New Capabilities

- `shell-bot`: ShellBot — a chat participant that can execute shell commands on demand before delivering a reply.
- `run-shell-tool`: `run_shell` tool definition — executes a shell command and returns combined stdout/stderr.
- `general-tool-bot`: `GeneralToolBot` — shared base class for single-round-trip tool-calling bots.

### Modified Capabilities

- `tool-bot`: ToolBot now inherits from GeneralToolBot instead of standing alone (no behaviour change, internal refactor only).
- `file-bot`: FileBot now inherits from GeneralToolBot instead of standing alone (no behaviour change, internal refactor only).

## Impact

- **`src/codemoo/core/tools/__init__.py`** — new `run_shell` tool exported.
- **`src/codemoo/core/bots/`** — new `general_tool_bot.py`; `tool_bot.py` and `file_bot.py` updated to inherit from it; new `shell_bot.py`.
- **`src/codemoo/core/bots/__init__.py`** — export `GeneralToolBot` and `ShellBot`.
- **`src/codemoo/__init__.py`** — register `ShellBot` as "Ash" with the 🐚 emoji.
- **`tests/`** — new test files for `run_shell` tool and `ShellBot`; existing ToolBot/FileBot tests remain green.
- No API or dependency changes; `subprocess` is stdlib.
