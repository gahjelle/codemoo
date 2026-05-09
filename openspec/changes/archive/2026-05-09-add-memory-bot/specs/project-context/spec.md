## ADDED Requirements

### Requirement: context.py exposes a MemoryLoadEvent dataclass
A `MemoryLoadEvent` frozen dataclass SHALL exist in `core/context.py` with the same fields as `ContextLoadEvent`: `bot_name: str`, `source: str` (always `"file"` for memory), `path: str` (the memory file path as a string), and `content: str` (the full memory file contents).

#### Scenario: MemoryLoadEvent has the correct fields
- **WHEN** `MemoryLoadEvent(bot_name="Aura", source="file", path=".codemoo/memory.md", content="# Memory")` is constructed
- **THEN** all four fields SHALL be accessible on the instance

### Requirement: context.py exposes a read_memory_file function
A `read_memory_file(memory_file_path: Path, bot_name: str, commentator: CommentatorBot) -> str | None` function SHALL exist in `core/context.py`. It SHALL read the file at `memory_file_path` if it exists, emit a `MemoryLoadEvent` to the commentator on success, and return the contents. If the file does not exist or reading fails, it SHALL return `None` without raising.

#### Scenario: read_memory_file reads an existing file
- **WHEN** `read_memory_file` is called with a path pointing to an existing file
- **THEN** it SHALL return the file's contents as a string
- **AND** emit a `MemoryLoadEvent` to the commentator

#### Scenario: read_memory_file returns None when file absent
- **WHEN** `read_memory_file` is called with a path to a non-existent file
- **THEN** it SHALL return `None`
- **AND** no `MemoryLoadEvent` is emitted

#### Scenario: read_memory_file returns None on read error
- **WHEN** reading the file raises any exception
- **THEN** `read_memory_file` SHALL return `None` without raising
- **AND** no `MemoryLoadEvent` is emitted
