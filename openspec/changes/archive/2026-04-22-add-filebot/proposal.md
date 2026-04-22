## Why

The demo chain has five bots (EchoBot → ToolBot) but stops before the bot can touch the filesystem. FileBot is the sixth step, adding a `read_file` tool so the LLM can inspect real files on demand — the first moment the bot interacts with the outside world beyond calculation.

## What Changes

- Add a `read_file` tool definition to the tools module — given a path, returns the file's text content
- Add `FileBot`, a bot pre-configured with `read_file` and file-oriented system instructions
- Register FileBot in the CLI bot-selection screen

## Capabilities

### New Capabilities

- `file-bot`: The sixth demo bot; wraps ToolBot with a `read_file` tool and file-aware system instructions
- `read-file-tool`: A `ToolDef` that accepts a file path and returns file contents as a string

### Modified Capabilities

- `tool-definitions`: New `read_file` tool exported alongside `reverse_string`

## Impact

- `src/codemoo/core/tools/__init__.py` — add `read_file` tool definition and export
- `src/codemoo/core/bots/` — add `file_bot.py`
- `src/codemoo/cli.py` — register FileBot in the bot list
- `tests/` — new unit tests for `read_file` tool and FileBot
