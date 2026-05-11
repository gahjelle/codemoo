## Why

All three MemoryBot variants share the same memory file, causing cross-domain leakage: coding preferences (e.g. "uses uv for Python") bleed into office contexts (m365, workspace), adding irrelevant noise to the LLM's system prompt. Office preferences are also user-level concerns that should persist across projects, not be confined to a single project's `.codemoo/` folder.

## What Changes

- `code` variant memory file renamed from `memory.md` to `memory-code.md` (stays in `{project_settings_path}`)
- `m365` variant memory file moved from `{project_settings_path}/memory.md` to `{user_settings_path}/memory-m365.md`
- `workspace` variant memory file moved from `{project_settings_path}/memory.md` to `{user_settings_path}/memory-workspace.md`
- `.gitignore` updated from `.codemoo/memory.md` to `.codemoo/memory-code.md`
- Existing `memory.md` files in `.codemoo/` and `demo/.codemoo/` renamed to `memory-code.md`

## Non-goals

- No migration of m365/workspace memory contents (clean break is acceptable)
- No new template tokens in the config system (`{variant}` is not needed; paths are defined literally per variant)
- No changes to how memory is loaded, saved, or injected into the system prompt

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `memory-bot`: Memory file paths now differ by variant — `code` stays project-scoped, `m365` and `workspace` move to user-scoped storage with variant-specific filenames

## Impact

- `src/codemoo/config/codemoo.toml`: three `memory_file` values updated
- `.gitignore`: one line updated
- `.codemoo/memory.md` → `.codemoo/memory-code.md` (rename)
- `demo/.codemoo/memory.md` → `demo/.codemoo/memory-code.md` (rename)
- No code changes required — path resolution already supports `{user_settings_path}`
