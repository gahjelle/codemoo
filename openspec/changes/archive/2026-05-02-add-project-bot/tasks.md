## 1. Context Reading Infrastructure

- [x] 1.1 Create `src/codemoo/core/context.py` with ContextLoadEvent dataclass
- [x] 1.2 Add `read_project_context()` async function that reads from file or SharePoint
- [x] 1.3 Implement file reading with graceful error handling (returns None on failure)
- [x] 1.4 Implement SharePoint reading using existing `_read_sharepoint()` function
- [x] 1.5 Emit ContextLoadEvent to commentator on successful read

## 2. Commentator Integration

- [x] 2.1 Update `comment()` method in CommentatorBot to accept ContextLoadEvent
- [x] 2.2 Add `_comment_on_context()` method to generate context loading commentary
- [x] 2.3 Format context preview (first 200 chars) for commentary prompt
- [x] 2.4 Handle exceptions gracefully with fallback message

## 3. ProjectBot Implementation

- [x] 3.1 Create `src/codemoo/core/bots/project_bot.py`
- [x] 3.2 Add GuardBot-style approval types (Approved, Denied, ApprovalRequest)
- [x] 3.3 Add `_denial_message()` and `_async_approved()` helper functions
- [x] 3.4 Create ProjectBot dataclass with context_source field
- [x] 3.5 Implement `register_guard()` method
- [x] 3.6 Implement `on_message()` that calls `read_project_context()` and injects into system prompt
- [x] 3.7 Duplicate GuardBot tool loop logic (while True loop with approval gates)

## 4. Configuration Schema

- [x] 4.1 Add `"ProjectBot"` to BotType literal in `config/schema.py`
- [x] 4.2 Create ContextSource dataclass with `type: Literal["file", "sharepoint"]` and `name: str`
- [x] 4.3 Add `context_source: ContextSource | None` to BotVariantConfig
- [x] 4.4 Add `context_source: dict[str, str] | None` to ResolvedBotConfig dataclass
- [x] 4.5 Update `resolve()` function to pass context_source from variant to ResolvedBotConfig

## 5. Bot Registry

- [x] 5.1 Import ProjectBot in `core/bots/__init__.py`
- [x] 5.2 Add "ProjectBot" to __all__ list
- [x] 5.3 Add ProjectBot case to `_make_bot()` function with context_source parameter

## 6. Demo Context File

- [x] 6.1 Create `demo/AGENTS.md` with project description
- [x] 6.2 Add development commands section (uv run greeter.py, uv run pytest test_greeter.py)
- [x] 6.3 Document intentional bugs (encoding issue, README/code mismatch)
- [x] 6.4 Add note about preserving intentional issues

## 7. Bot Configuration

- [x] 7.1 Add ProjectBot entry to `codemoo.toml` with name "Lore" and emoji "OPEN BOOK"
- [x] 7.2 Create `variants.code` with `context_source = { type = "file", name = "AGENTS.md" }` and code tools
- [x] 7.3 Create `variants.business` with `context_source = { type = "sharepoint", name = "TEAM.md" }` and M365 tools
- [x] 7.4 Add example prompts for both variants

## 8. Documentation

- [x] 8.1 Add ProjectBot row to bot names table in BOTS.md (with emoji, name rationale)
- [x] 8.2 Add ProjectBot to business progression table in BOTS.md
- [x] 8.3 Verify README.md doesn't need updates (ProjectBot is part of planned bots, README shows currently implemented bots)

## 9. Verification

- [x] 9.1 Run `uv run ruff format .` on all modified files
- [x] 9.2 Run `uv run ruff check .` and fix any issues
- [x] 9.3 Run `uv run ty check .` and fix any type errors
- [x] 9.4 Run `uv run pytest` to ensure no regressions
- [x] 9.5 Test ProjectBot manually: run from demo/ directory and verify AGENTS.md is loaded
- [x] 9.6 Verify commentator shows context loading event
- [x] 9.7 Test graceful degradation: run from different directory without AGENTS.md
