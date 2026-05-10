## ADDED Requirements

### Requirement: demo/AGENTS.md provides project context for ProjectBot

`demo/AGENTS.md` SHALL be present in the demo directory and SHALL describe the
greeter project — its purpose, development commands, and the intentional issues
(ascii encoding bug, README/code discrepancy). This file is read by ProjectBot
as its `context_source` when running in the code variant. Its content SHALL be
consistent with the actual state of greeter.py and test_greeter.py.

#### Scenario: AGENTS.md is readable and describes the project
- **WHEN** `demo/AGENTS.md` is read
- **THEN** it SHALL describe the greeter project and list `uv run greeter.py`
  and `uv run pytest test_greeter.py` as development commands

#### Scenario: AGENTS.md documents the intentional issues
- **WHEN** `demo/AGENTS.md` is read
- **THEN** it SHALL mention the `encoding="ascii"` bug and the README/sorting
  discrepancy as intentional demo artifacts that SHALL NOT be fixed unless asked

### Requirement: demo/.codemoo/memory.md is empty at demo start

`demo/.codemoo/memory.md` SHALL exist but SHALL be empty (zero bytes or
whitespace only) at the start of each demo run. This ensures MemoryBot's
"What do you know about me?" prompt produces an empty response, which is
required for the MemoryBot arc (learn color preference → apply it).

#### Scenario: Memory file exists but is empty before demo
- **WHEN** a demo run begins
- **THEN** `demo/.codemoo/memory.md` SHALL exist and SHALL contain no
  substantive content

#### Scenario: Stale memory does not leak into the demo
- **WHEN** a previous demo run wrote preferences to memory.md
- **THEN** the file SHALL be cleared before the next demo run so MemoryBot
  has no prior knowledge of user preferences
