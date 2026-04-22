## 1. GeneralToolBot base class

- [x] 1.1 Create `src/codemoo/core/bots/general_tool_bot.py` with `GeneralToolBot` dataclass: fields `name`, `emoji`, `backend`, `human_name`, `tools`, `instructions` (no default), `max_messages=20`, `is_human: ClassVar[bool] = False`, and the full `on_message` implementation with `_tool_name` helper
- [x] 1.2 Export `GeneralToolBot` from `src/codemoo/core/bots/__init__.py`

## 2. Refactor ToolBot and FileBot

- [x] 2.1 Update `tool_bot.py`: inherit from `GeneralToolBot`, remove duplicate fields and `on_message`/`_tool_name`, keep only the module docstring, `_INSTRUCTIONS` constant, and re-declared `instructions: str = _INSTRUCTIONS`
- [x] 2.2 Update `file_bot.py`: same refactor — inherit from `GeneralToolBot`, keep only docstring, `_INSTRUCTIONS`, and re-declared `instructions: str = _INSTRUCTIONS`
- [x] 2.3 Run existing ToolBot and FileBot tests and confirm they still pass

## 3. run_shell tool

- [x] 3.1 Add `run_shell` `ToolDef` to `src/codemoo/core/tools/__init__.py`: uses `subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)`, returns a formatted string with exit code, stdout, and stderr; catches `subprocess.TimeoutExpired` and returns a timeout message
- [x] 3.2 Add `run_shell` to `__all__` in `src/codemoo/core/tools/__init__.py`
- [x] 3.3 Write `tests/core/tools/test_run_shell.py`: test successful command returns stdout, failing command returns non-zero exit code without raising, timeout returns timeout message, schema has correct top-level fields

## 4. ShellBot

- [x] 4.1 Create `src/codemoo/core/bots/shell_bot.py`: `ShellBot(GeneralToolBot)` with `_INSTRUCTIONS` mentioning `run_shell`, re-declared `instructions: str = _INSTRUCTIONS`, appropriate class docstring
- [x] 4.2 Export `ShellBot` from `src/codemoo/core/bots/__init__.py`
- [x] 4.3 Write `tests/core/bots/test_shell_bot.py` mirroring `test_file_bot.py`: test `is_human`, text-response path, tool-use path, tool list forwarded to `complete_step`, system prompt mentions `run_shell`

## 5. Registration

- [x] 5.1 Import `run_shell` in `src/codemoo/__init__.py` and add `ShellBot` entry with `name="Ash"`, `emoji="\N{SPIRAL SHELL}"`, and `tools=[run_shell]` after the `FileBot` entry

## 6. Documentation

- [x] 6.1 Update `SCRIPT.md`: fill in the name "Ash" in the Full Progression and Bot Emojis tables for ShellBot (row 7)
