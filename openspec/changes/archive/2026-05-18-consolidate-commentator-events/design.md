## Context

`CommentatorBot` currently handles six distinct frozen dataclasses: `ToolCallEvent`, `ValidationBlockEvent`, `ToolErrorEvent`, `ContextLoadEvent`, `MemoryLoadEvent`, and `BotRestartEvent`. The `comment()` method is a six-branch isinstance chain with one `_comment_on_X` private method per event type.

Three problems drive this change:

1. **Double-narration on blocked tools.** Bots emit `ToolCallEvent` before calling `dispatch_tool`, which then independently emits `ValidationBlockEvent` if validation fails. The viewer hears "X is calling write_file" immediately followed by "Blocked: path escapes sandbox" — two commentary bubbles for one failed attempt.

2. **Hardcoded prompt templates.** Each `_comment_on_X` method contains a hand-crafted f-string prompt. Adding a new event type or tuning commentary phrasing requires editing Python, not config.

3. **Growing import surface.** Bots import `ToolCallEvent` explicitly; `dispatch_tool` does two lazy local imports to avoid circular dependencies. Any new event type adds to this surface.

## Goals / Non-Goals

**Goals:**
- Consolidate `ToolCallEvent`, `ValidationBlockEvent`, `ToolErrorEvent` into `ToolEvent(outcome)`.
- Consolidate `ContextLoadEvent`, `MemoryLoadEvent` into `LoadEvent(kind)`.
- Move all tool-related commentator emission into `dispatch_tool` as the single dispatch point.
- Move the five event prompt templates into config text files, loaded at startup.
- Leave `BotRestartEvent` and its hardcoded prompt unchanged.

**Non-Goals:**
- Changing commentary tone, persona behavior, or fallback logic.
- Adding new event types or template variables.
- Modifying the `BotRestartEvent` prompt or data shape.

## Decisions

### 1. `ToolEvent` with `outcome: Literal["call", "blocked", "error"]` and `detail: str | None`

**Chosen over**: keeping three separate dataclasses.

The three tool events share `bot_name`, `tool_name`, `arguments`; they differ only in which extra field is present (`reason` for blocked, `result` for error, nothing for call). A single class with an `outcome` discriminator and an optional `detail: str | None` captures this cleanly.

The Optional `detail` field is not a type-safety problem here because consumption always flows through `str.format()` placeholders: `{detail}` in a template, substituted as `event.detail or ""`. The template for `"call"` simply won't include `{detail}`. There is no assertion-heavy code path where a None slips through unexpectedly.

`@typing.overload` on classmethods could enforce construction correctness (blocked always requires detail), but the overhead isn't worth it for an internal system with three call sites.

### 2. `dispatch_tool` emits `ToolEvent(outcome="call")` after validation passes

**Chosen over**: emitting "call" before validation (current bot behavior), or not emitting "call" at all.

Emitting after validation means "call" is the announcement of actual tool execution, not an announcement of an attempt that might be blocked. Together with "blocked" being the exclusive event on validation failure, this gives one event per dispatch — no double-narration.

The `commentator` parameter already appears in every bot's `dispatch_tool` call, so the bot code still shows a `commentator` field even after the explicit `commentator.comment(...)` call is removed. The demo pedagogical signal ("bots carry a commentator") is preserved.

### 3. Template loading via `_resolve_commentary_template_refs()` in `config/__init__.py`

**Chosen over**: `CommentatorBot` loading files at construction time.

Consistent with how persona instructions are resolved: `codemoo.toml` declares `[commentary_templates]` with `tool_call = "tool_call.txt"` etc.; `_resolve_commentary_template_refs()` reads them; `CodemooConfig.commentary_templates` holds `dict[str, str]` of loaded content. `CommentatorBot` receives a plain dict — no file I/O at construction.

Template files live in `src/codemoo/config/commentary_templates/`. The template keys are the outcome/kind strings used as lookup keys at runtime: `"call"`, `"blocked"`, `"error"`, `"context"`, `"memory"`.

### 4. `str.format()` for template variable substitution

**Chosen over**: Jinja2 or other template engines.

No new dependency, consistent with project minimalism. The substitution variables per event type are:

| Template key | Variables |
|---|---|
| `call` | `{bot_name}`, `{tool_name}`, `{sig}` |
| `blocked` | `{bot_name}`, `{tool_name}`, `{sig}`, `{detail}` |
| `error` | `{bot_name}`, `{tool_name}`, `{sig}`, `{detail}` |
| `context` | `{bot_name}`, `{source_desc}`, `{content_len}`, `{preview}` |
| `memory` | `{bot_name}`, `{path}`, `{content_len}`, `{preview}` |

`CommentatorBot._comment_on_tool()` and `_comment_on_load()` always pass all variables for the event type; unused `{placeholders}` in the template are simply absent.

## Risks / Trade-offs

**Breaking change on old event classes** → All five removed types are internal. No public API. Update all five bots and `context.py` mechanically in one pass; tests that reference old types must also update.

**Single `_comment_on_tool()` branches on `outcome`** → The isinstance chain shortens (6 → 3 arms), but `_comment_on_tool` now has an inner branch on `outcome` to select `sig`-building and `dim_prefix` logic. Net complexity is similar, but outer API is simpler and extensible by config alone.

**Template file load failures at startup** → Missing or malformed template files will raise at config load time (same behavior as missing persona instruction files). This is fail-fast and correct.

**`detail or ""`** → If a `ToolEvent(outcome="blocked")` is somehow constructed without `detail`, the template renders an empty string rather than raising. This is acceptable: the fallback Streik message still fires on LLM failure, and a missing `detail` on a blocked event indicates a bug in the emitter.

## Open Questions

None. All decisions above are resolved.
