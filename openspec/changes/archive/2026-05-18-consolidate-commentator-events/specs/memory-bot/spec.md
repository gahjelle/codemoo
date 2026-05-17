## MODIFIED Requirements

### Requirement: Memory loading emits a commentator event
`read_memory_file()` in `core/context.py` SHALL emit a `LoadEvent(kind="memory")` to the commentator when the memory file is successfully read. `MemoryLoadEvent` is removed; `LoadEvent` from `commentary-events` is the replacement.

#### Scenario: LoadEvent emitted when memory file is present
- **WHEN** `read_memory_file()` successfully reads the memory file
- **THEN** a `LoadEvent(kind="memory", bot_name=..., source="file", path=str(memory_file_path), content=content)` SHALL be emitted to the commentator
- **AND** the event SHALL include the bot name, the string path to the memory file, and the full file content

#### Scenario: No LoadEvent when memory file is absent
- **WHEN** `read_memory_file()` finds no file at the given path
- **THEN** no `LoadEvent` SHALL be emitted
