## Why

Current bots (up to GuardBot/Cato) operate without any knowledge of the project they're working on. They make decisions based on their instructions and conversation history, but lack awareness of project-specific conventions, known issues, and domain knowledge. This leads to generic responses that may not respect project conventions or understand intentional design decisions.

ProjectBot (Lore) solves this by reading project context from a source file (AGENTS.md for code projects, SharePoint for business teams) and injecting it into the system prompt. This creates agents that "read the room" before acting.

## What Changes

- **New bot**: ProjectBot (Lore) that loads project context before acting
- **New shared utility**: `read_project_context()` in `core/context.py` for reading from file or SharePoint
- **New commentator event**: ContextLoadEvent to narrate context loading
- **Config schema**: Add `context_source` field to bot variants
- **Demo context**: Create `demo/AGENTS.md` with demo-specific project information
- **Documentation**: Update BOTS.md with ProjectBot entry and business variant

## Capabilities

### New Capabilities

- `project-context`: Bots can load project-specific context from files (AGENTS.md) or SharePoint documents and inject it into their system prompt. Enables context-aware agent behavior with graceful degradation when context is unavailable.

### Modified Capabilities

None. This is a new capability that extends existing bot infrastructure.

## Impact

**New files**:
- `src/codemoo/core/context.py` — Shared context reading utility
- `src/codemoo/core/bots/project_bot.py` — ProjectBot implementation
- `demo/AGENTS.md` — Demo project context file

**Modified files**:
- `src/codemoo/core/bots/commentator_bot.py` — Add ContextLoadEvent handling
- `src/codemoo/core/bots/__init__.py` — Add ProjectBot to registry
- `src/codemoo/config/schema.py` — Add context_source to config schema
- `src/codemoo/config/codemoo.toml` — Add ProjectBot configuration
- `BOTS.md` — Add ProjectBot documentation

**Architecture**:
- ProjectBot duplicates GuardBot's tool loop logic (intentional for demo clarity)
- Context reading is extracted to shared utility for reuse by future bots (MemoryBot, SkillBot, etc.)
- No inheritance between bots — each is standalone for demo comparison

## Non-goals

- Caching context across messages (can be added later if performance becomes an issue)
- Automatic discovery of AGENTS.md by walking directory tree (explicit path is clearer)
- Multiple context sources per bot (one source per variant is sufficient)
- Modifying existing bot behavior (ProjectBot is a new capability, not a change to GuardBot)
