## Context

Codemoo currently has 11 bot types, progressing from simple echo to full agentic loop with guardrails. The most advanced bot, GuardBot (Cato), implements:
- Tool loop with multi-step execution
- Human-in-the-loop approval for destructive actions
- Commentator integration for visibility

ProjectBot (Lore) is the next evolution: GuardBot + context awareness. This design covers how to implement context loading without inheritance (for demo clarity) while extracting shared utilities for future reuse.

## Goals / Non-Goals

**Goals:**
- Add ProjectBot that reads project context before acting
- Support both file (AGENTS.md) and SharePoint context sources
- Enable graceful degradation when context is unavailable
- Provide commentator visibility into context loading
- Create shared `read_project_context()` utility for future bots
- Maintain standalone bot implementations for demo comparison

**Non-Goals:**
- Context caching (can be added later if needed)
- Automatic AGENTS.md discovery (explicit path is clearer)
- Multiple context sources per bot
- Modifying GuardBot or other existing bots

## Decisions

### Decision 1: Duplicate GuardBot logic instead of inheritance

**Chosen:** Duplicate the tool loop (~80 lines) in ProjectBot

**Alternatives considered:**
- Inheritance (`ProjectBot(GuardBot)`): Cleaner code, but makes demo comparison harder. Audience can't easily see "Lore is Cato + context" when reading the code.
- Shared tool loop function: Would require passing many parameters, obscures the bot logic

**Rationale:** For a demo project, code clarity beats DRY. Each bot file should be self-contained and readable. The duplication is contained to one method and unlikely to diverge.

### Decision 2: Extract context reading to shared utility

**Chosen:** Create `core/context.py` with `read_project_context()`

**Alternatives considered:**
- Inline in ProjectBot: Works, but future bots (MemoryBot, SkillBot) will need the same capability
- Put in tools module: Context reading isn't a tool the LLM calls — it's infrastructure

**Rationale:** Context reading is a cross-cutting concern. Extracting it makes ProjectBot simpler and enables reuse without code duplication across bots.

### Decision 3: Require commentator for context reading

**Chosen:** `read_project_context()` requires a CommentatorBot parameter

**Alternatives considered:**
- Optional commentator: Adds complexity, and all context-reading bots will use tools and thus have a commentator

**Rationale:** Cleaner API. Every bot that reads context will already have a commentator (they all use tools). No need for optional handling.

### Decision 4: Read context on every message

**Chosen:** No caching, read fresh on each message

**Alternatives considered:**
- Read once and cache: Would require session state management, unclear cache invalidation
- Cache with mtime check: Over-engineering for demo purposes

**Rationale:** Simpler implementation. File reads are fast (~1-2ms). SharePoint is slower (~200-500ms) but acceptable for demo. Can add caching later if performance becomes an issue.

### Decision 5: Use inline table for context_source

**Chosen:** Structured config: `{ type = "file", name = "AGENTS.md" }` or `{ type = "sharepoint", name = "TEAM.md" }`

**Alternatives considered:**
- Asymmetric string (`"AGENTS.md"` / `"sharepoint:TEAM.md"`): Simpler for common case, but no type validation at config load time
- Symmetric string with prefix (`"file:AGENTS.md"` / `"sharepoint:TEAM.md"`): Explicit but still string parsing at runtime

**Rationale:** Inline table enables Pydantic validation at config load time, catching errors early. It's extensible (can add fields like `site` for custom SharePoint sites later). The verbosity cost is paid once in config. Structured data is more Pythonic than string parsing.

## Risks / Trade-offs

**Risk: Code duplication in tool loop**
→ Mitigation: Accept it. The duplication is contained and both implementations are stable. Future refactoring can extract if needed.

**Risk: SharePoint latency on every message**
→ Mitigation: Accept for now. Demo usage is limited. Can add caching later if needed.

**Risk: Context file grows large**
→ Mitigation: No limit currently. Large contexts increase token usage. Consider adding length limit or summarization in future.

**Risk: Graceful degradation hides config errors**
→ Mitigation: With inline table config, invalid types are caught at load time. Users can check commentator output to see if context was loaded.

**Risk: AGENTS.md missing in demo folder**
→ Mitigation: Create demo/AGENTS.md as part of implementation. Demo instructions already specify running from demo/ directory.

## Implementation Outline

1. Create `core/context.py` with ContextLoadEvent and read_project_context()
2. Update CommentatorBot to handle ContextLoadEvent
3. Create ProjectBot class (duplicate GuardBot + context injection)
4. Add ContextSource dataclass and context_source field to config schema
5. Add ProjectBot to bot registry in __init__.py
6. Create demo/AGENTS.md
7. Add ProjectBot configuration to codemoo.toml (with inline table for context_source)
8. Update BOTS.md documentation
