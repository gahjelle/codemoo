## 1. Dependencies and Module Structure

- [x] 1.1 Add `google-auth-oauthlib` using `uv add google-auth-oauthlib`
- [x] 1.2 Create `src/codemoo/workspace/__init__.py`
- [x] 1.3 Create `src/codemoo/workspace/auth.py` with Google OAuth2 console flow
- [x] 1.4 Create `src/codemoo/workspace/tools/__init__.py` with WORKSPACE_TOOL_REGISTRY
- [x] 1.5 Add `workspace_token_path` to PathsConfig in schema.py
- [x] 1.6 Add `[workspace]` config section to codemoo.toml with client_id, client_secret, scopes

## 2. M365 Tool Renaming (Breaking Change)

- [x] 2.1 Rename `list_email` → `list_outlook_email` in m365/tools/read.py
- [x] 2.2 Rename `read_email` → `read_outlook_email` in m365/tools/read.py
- [x] 2.3 Rename `send_email` → `send_outlook_email` in m365/tools/write.py
- [x] 2.4 Rename `list_calendar` → `list_outlook_calendar` in m365/tools/read.py
- [x] 2.5 Rename `create_calendar_event` → `create_outlook_calendar_event` in m365/tools/write.py
- [x] 2.6 Rename `list_sharepoint` → `list_sharepoint` in m365/tools/read.py (already correct)
- [x] 2.7 Rename `read_sharepoint` → `read_sharepoint` in m365/tools/read.py (already correct)
- [x] 2.8 Rename `write_sharepoint` → `write_sharepoint` in m365/tools/write.py (already correct)
- [x] 2.9 Rename `post_teams_message` → `post_teams_message` in m365/tools/write.py (already correct)
- [x] 2.10 Update all tool name references in M365_TOOL_REGISTRY

## 3. Workspace Tools Implementation

- [x] 3.1 Create `workspace/tools/read.py` with list_gmail, read_gmail, list_gcal tools
- [x] 3.2 Create `workspace/tools/write.py` with send_gmail, create_gcal_event, post_chat_message tools
- [x] 3.3 Implement Gmail body extraction helper for multipart messages
- [x] 3.4 Add init hook `_init_workspace` that triggers Google OAuth
- [x] 3.5 Register all tools in WORKSPACE_TOOL_REGISTRY with init hook

## 4. Core Integration

- [x] 4.1 Update `core/bots/__init__.py` to import WORKSPACE_TOOL_REGISTRY
- [x] 4.2 Merge WORKSPACE_TOOL_REGISTRY into _ALL_TOOLS
- [x] 4.3 Create PLATFORM_REGISTRIES constant in frontends/tui.py
- [x] 4.4 Update `_run_init_hooks_for_resolved` to check all platform registries

## 5. Configuration Updates

- [x] 5.1 Rename `[scripts.m365]` variants from `business` → `m365` in codemoo.toml
- [x] 5.2 Rename `[scripts.m365_lite]` variants from `business_lite` → `m365_lite`
- [x] 5.3 Add `[scripts.workspace]` configuration with workspace variants
- [x] 5.4 Add `[scripts.workspace_lite]` configuration with workspace_lite variants
- [x] 5.5 Update all bot variant definitions to use new naming (m365, m365_lite, workspace, workspace_lite)
- [x] 5.6 Update tool lists in variant configs to use new prefixed tool names

## 6. Test Updates

- [x] 6.1 Update tests referencing old tool names to new prefixed names
- [x] 6.2 Add tests for workspace tool registry structure
- [x] 6.3 Add tests for workspace init hook
- [x] 6.4 Update bot variant tests to use new naming

## 7. Verification

- [x] 7.1 Run `uv run ruff check .` and fix all issues
- [x] 7.2 Run `uv run ruff format .` and verify formatting
- [x] 7.3 Run `uv run ty check .` and fix type errors
- [x] 7.4 Run `uv run pytest` and ensure all tests pass

## 8. Documentation

- [x] 8.1 Review and update README.md with workspace platform info
- [x] 8.2 Review and update AGENTS.md if tool naming conventions changed
- [x] 8.3 Review PLANS.md and BOTS.md for any needed updates
