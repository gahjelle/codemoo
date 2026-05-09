## Context

The demo progression currently ends at ProjectBot (Lore), which loads a static, human-written context file (AGENTS.md / TEAM.md) once at startup. The next step in Act 5 is MemoryBot (Aura): a bot that reads and writes its own memory file, building a persistent model of the user's preferences across sessions.

MemoryBot copies the ProjectBot pattern (context loaded at startup, injected into every system prompt, full tool loop with approval gates) and extends it with:
1. A second context source — the bot's own memory file.
2. A `save_memory` tool — the LLM's mechanism for writing to that file.

All bots in the codebase follow a no-inheritance pattern: each bot is a self-contained dataclass copied from the one before it. MemoryBot follows this convention.

## Goals / Non-Goals

**Goals:**
- Add MemoryBot as a new bot type with code, m365, and workspace variants.
- Load a project-scoped memory file (`.codemoo/memory.md`) at startup alongside project context.
- Provide a `save_memory(content: str)` tool that the LLM calls explicitly; the path is pre-baked at construction time.
- Emit `MemoryLoadEvent` on successful memory load, consistent with `ContextLoadEvent`.
- Add `user_settings_path` and `project_settings_path` to the config's `parse_dynamic` extra dict so `.codemoo/` paths can be referenced from TOML.

**Non-Goals:**
- User-scoped memory via platformdirs (infrastructure is added, but memory stays project-scoped for this change).
- Automatic memory persistence without an explicit LLM tool call.
- A `MemorySaveEvent` — the tool call appearing in the tracer is sufficient for demo visibility.
- Structured/schema-enforced memory format — free-form Markdown only.
- MemoryBot inheriting from ProjectBot.

## Decisions

### 1. Dedicated `save_memory` tool, not `write_file`

**Decision:** Create a new `save_memory` ToolDef via `make_memory_tool(path)` rather than relying on the existing `write_file` tool with a cleverly worded system prompt.

**Rationale:** The tool name appears in the tracer. `save_memory` is the demo's teaching moment — the audience sees the LLM deciding what's worth remembering. `write_file` would muddy that signal. A dedicated tool also locks the path at construction time, so the LLM cannot write memory anywhere except the pre-configured location.

**Alternative considered:** Add a `memory_path` argument to `write_file` and validate it against the memory file path. Rejected: adds complexity to the general-purpose file tool and still shows `write_file` in the trace.

### 2. Replace semantics for `save_memory`

**Decision:** `save_memory(content: str)` overwrites the entire memory file with `content`.

**Rationale:** Replace semantics allow the LLM to curate memory over time — pruning stale facts, revising incorrect observations. Append-only memory grows unbounded and loses the ability to correct errors. The full memory content is visible in the tool call trace, which is educational.

**Alternative considered:** Append semantics (`save_memory(fact: str)` appends one line). Rejected: the LLM cannot prune or restructure; memory degrades over time.

### 3. Tool injected at construction, not registered in TOOL_REGISTRY

**Decision:** `make_memory_tool(path: Path) -> ToolDef` is called in `_make_bot` and the result is appended to the tools list. The `save_memory` tool is NOT listed in `TOOL_REGISTRY` or the TOML `tools` array.

**Rationale:** Unlike `read_file` / `write_file`, there is no meaningful "raw" version of `save_memory` — the path is integral to the tool's identity. The existing file tools have a path-agnostic form in the registry because they accept a path argument. `save_memory` does not. Injecting at construction is cleaner: no dummy registry entry, no `_sandbox` special case.

**Alternative considered:** Add a raw `save_memory` to `TOOL_REGISTRY` with a placeholder path and patch it in `_sandbox`. Rejected: a tool with a placeholder path that must always be overridden is misleading.

### 4. Project-scoped memory via `.codemoo/memory.md`

**Decision:** Memory lives at `session_folder / ".codemoo" / "memory.md"`, referenced in TOML as `{project_settings_path}/memory.md`.

**Rationale:** Project-scoped memory is tangible and inspectable during a demo — you can open `.codemoo/memory.md` on screen and show the audience exactly what Aura has learned. The `.codemoo/` folder establishes a namespace for bot artifacts within a project (future candidates: SkillBot playbooks, CommandBot shortcuts). `make_memory_tool` creates the directory on first write if needed.

**Alternative considered:** User-scoped memory via `platformdirs.user_data_dir("codemoo")`. Rejected for now: less visible during a live demo, cross-project contamination risk. `user_settings_path` is added to the config infrastructure so user-scoped memory can be introduced later without further config surgery.

### 5. `MemoryLoadEvent` mirrors `ContextLoadEvent`

**Decision:** Add `MemoryLoadEvent` to `core/context.py` with the same fields as `ContextLoadEvent` (`bot_name`, `source`, `path`, `content`). Add `read_memory_file(path, bot_name, commentator)` alongside `read_project_context`.

**Rationale:** Consistency with the existing pattern. The commentator/tracer already knows how to handle `ContextLoadEvent`; a parallel event structure requires no new UI work. Placing it in `context.py` keeps the context-loading utilities co-located.

## Risks / Trade-offs

**Memory file grows large across many sessions** → Mitigated by replace semantics: the LLM can prune during each save. System prompt encourages concise memory.

**LLM may not call save_memory reliably** → By design. Explicit tool use is the mechanism — this is the teaching point. If the LLM doesn't call it, nothing is persisted. No silent magic.

**`.codemoo/` directory doesn't exist on first write** → `make_memory_tool` calls `path.parent.mkdir(parents=True, exist_ok=True)` before writing.

**Memory file path escapes session folder** → Not possible: `make_memory_tool` receives an absolute path constructed from `session_folder` (or the expanded `{project_settings_path}`). The path is never provided by the LLM.

## Open Questions

None — all design decisions resolved during exploration.
