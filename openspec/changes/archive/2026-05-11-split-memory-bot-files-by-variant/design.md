## Context

MemoryBot's memory file path is configured per-variant in `codemoo.toml` using the `memory_file` field with template tokens (`{project_settings_path}`, `{user_settings_path}`). Both tokens are already resolved at config load time in `src/codemoo/config/__init__.py`. The bot factory in `core/bots/__init__.py` converts the resolved string to a `Path` and passes it to `make_memory_tool`. No code changes are needed — the existing infrastructure already supports per-variant paths with user-scoped storage.

Current state: all three variants point to `{project_settings_path}/memory.md` (i.e. `.codemoo/memory.md` in the working directory).

## Goals / Non-Goals

**Goals:**
- Eliminate cross-domain memory leakage between coding and office contexts
- Move office memory to user-level scope so it persists across projects
- Keep the change purely config/file-level with no code changes

**Non-Goals:**
- Migrating existing m365/workspace memory content to the new path
- Introducing a `{variant}` template token
- Changing how memory is loaded, saved, or injected

## Decisions

### Decision: Literal paths per variant, no new template token

The `{variant}` token was considered but rejected. Each variant's path is already defined in its own TOML block, so literal filenames (`memory-code.md`, `memory-m365.md`, `memory-workspace.md`) are simpler and more explicit. A token would add infrastructure for marginal benefit.

### Decision: code stays project-scoped, office moves to user-scoped

Coding memory is inherently project-specific (e.g. which tools the project uses). Office memory (email tone, calendar habits) is user-level and should follow the user across projects. The existing `{user_settings_path}` token resolves to `platformdirs.user_data_dir("codemoo")`, making this a one-word change per office variant.

### Decision: Rename code variant file rather than leaving it as `memory.md`

Renaming to `memory-code.md` makes the convention consistent across all variants and avoids ambiguity if new variants are added. The `.gitignore` entry and any existing files are updated in the same change.

## Risks / Trade-offs

- **Stale old files**: `.codemoo/memory.md` files not renamed manually will persist silently on other machines. → Acceptable; old file is simply unused, and the rename is a one-time local operation.
- **Lost office memory**: Existing `memory.md` content relevant to m365/workspace is not migrated. → Acceptable given clean-break policy; Aura will rebuild memory in a session or two.
- **platformdirs path varies by OS**: `user_data_dir("codemoo")` resolves differently on macOS, Linux, Windows. → Already a known property of `{user_settings_path}`; no new risk introduced.

## Migration Plan

1. Rename `.codemoo/memory.md` → `.codemoo/memory-code.md` in repo root and `demo/`
2. Update `.gitignore`
3. Update the three `memory_file` values in `codemoo.toml`
4. No rollback needed — reverting the TOML is sufficient to restore old behavior
