## 1. read_file Tool

- [x] 1.1 Add `read_file` tool definition to `src/codemoo/core/tools/__init__.py` (schema + fn that returns file contents or error string on failure)
- [x] 1.2 Export `read_file` in `__all__` alongside `ToolDef` and `reverse_string`
- [x] 1.3 Write unit tests for `read_file.fn`: existing file, non-existent path, and unreadable file (error string, not exception)
- [x] 1.4 Write unit test verifying `read_file.schema` has required fields (`type`, `name`, `description`, `parameters` with `path` in `required`)

## 2. FileBot

- [x] 2.1 Create `src/codemoo/core/bots/file_bot.py` with `FileBot` dataclass following the same structure as `ToolBot`
- [x] 2.2 Set `FileBot` default `instructions` to a file-aware system prompt mentioning `read_file`
- [x] 2.3 Write unit tests for `FileBot`: `is_human` is `False`, text response path, tool-use response path, sender name on reply

## 3. CLI Registration

- [x] 3.1 Add a `file` command to `src/codemoo/cli.py` that wires `FileBot` with the `read_file` tool and a Mistral backend
