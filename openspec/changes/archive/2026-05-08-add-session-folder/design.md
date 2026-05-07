## Context

Codemoo's tool execution is currently unbounded: `read_file`, `write_file`, `list_files`, and `run_shell` accept arbitrary paths and commands with no scope restriction. The `ToolDef` dataclass holds a `fn` callable, a `requires_approval` flag, and an `init` hook — but no concept of a validity check that runs before `fn`.

All bots that dispatch tools call `tool.fn(**response.arguments)` directly (or via GuardBot's approval gate before the call). There are four dispatch sites across `SingleTurnToolBot`, `AgentBot`, `GuardBot`, and `ProjectBot`.

The session folder is implicitly the process working directory, but nothing enforces it. `context.py`'s file-based AGENTS.md lookup uses `Path(source_name)` which silently resolves relative to wherever the process was launched from.

## Goals / Non-Goals

**Goals:**
- Introduce a `session_folder: Path` (= `Path.cwd()` at startup) passed explicitly through the bot construction chain.
- Add a `validate` field to `ToolDef` that is checked before `fn`; a non-`None` return hard-blocks the call.
- Centralise dispatch in a single `dispatch_tool()` async helper so validate + commentator wiring is written once.
- Sandbox `read_file`, `write_file`, `list_files` via path resolution; sandbox `run_shell` via token scanning.
- Emit a `ValidationBlockEvent` with LLM colour commentary when a call is blocked.
- Anchor file-based AGENTS.md lookup to the session folder.

**Non-Goals:**
- A `--path` CLI flag to override the session folder.
- Session history or project settings storage.
- Whitelisting specific paths (e.g. `/tmp`).
- Network or environment variable sandboxing.
- Sandboxing M365 or Google Workspace tools.

## Decisions

### D1 — Session folder as an explicit parameter, not a global

**Decision:** `session_folder` flows as a parameter: `make_bots(..., session_folder)` → `_make_bot(..., session_folder)`. Not a module-level singleton.

**Rationale:** A global mirrors how `config` works but makes testing harder and violates the Functional Core / Imperative Shell principle. Explicit parameters keep `_make_bot` a pure function of its inputs and allow tests to pass arbitrary paths without patching globals.

**Alternative considered:** Module-level `SESSION_FOLDER` set at startup (like `config`). Rejected: introduces ambient state that all tool modules would depend on implicitly.

### D2 — `validate` on `ToolDef`, not a `validators` list

**Decision:** `validate: Callable[..., str | None] | None = None` — a single optional callable, not a list.

**Rationale:** No current use case requires chaining multiple validators on one tool. A single callable keeps `ToolDef` simple; if chaining is ever needed, a wrapper that calls multiple validators in sequence satisfies it without changing the field type.

**Alternative considered:** `validators: list[Callable]`. Rejected: adds a visible list field to a dataclass the demo audience reads, with no immediate benefit.

### D3 — `dispatch_tool()` async helper instead of inline validation in `on_message()`

**Decision:** A standalone `async def dispatch_tool(tool, arguments, bot_name, commentator)` in `core/tools/` replaces `tool.fn(**args)` at all four dispatch sites.

**Rationale:** The commentator is async and lives on the bot, not on the tool. Inlining the validate + comment logic in each `on_message()` would add ~6 lines of infrastructure to methods that are pedagogically important in the demo. A named helper keeps each `on_message()` change to a single line and the logic in one place.

**Alternative considered:** Wrapping `fn` at construction time to include validation. Rejected: `fn` is sync; `commentator.comment()` is async; bridging would require either making `fn` async (large change) or fire-and-forget hacks.

### D4 — Validators applied at bot construction, not at tool definition time

**Decision:** Sandboxed `ToolDef` instances are created in `_make_bot()` via `dataclasses.replace(tool, validate=make_validator(session_folder))`. The module-level `ToolDef` constants in `files.py` and `shell.py` stay unchanged.

**Rationale:** The session folder is not known at module import time. Keeping tool definitions pure makes them reusable and independently testable. The wrapping at `_make_bot` is the right seam: it is where all bot-specific configuration is assembled.

### D5 — Shell validation via `shlex.split` token scanning, fail closed

**Decision:** Tokenise with `shlex.split(command)`; flag tokens starting with `/` (excluding `./`) or `..`. `shlex.ParseError` is treated as a block (fail closed).

**Rationale:** Full shell AST parsing is intractable. Token scanning catches the majority of straightforward escape attempts (absolute paths, `../` traversal, redirection targets). Known false negatives (paths inside quoted strings, `$()` subshells, variable expansion) are documented as limitations — an LLM generating benign commands will not hit them, and they cannot bypass the file tool validators anyway.

**Alternative considered:** Regex scan on the raw command string. Rejected: `shlex.split` correctly handles quoting, so e.g. `"../foo bar"` tokenises to one token rather than two fragments.

### D6 — Hard block before approval modal for `requires_approval` tools

**Decision:** `dispatch_tool()` is called inside the approved branch of `GuardBot` and `ProjectBot`. If `validate` fires, the error is returned without the call reaching `fn`; the approval modal has already been shown at that point.

**Rationale:** The approval modal is a human oversight mechanism for risky-but-permitted calls. A validation block means the call is not permitted regardless. The ordering (modal → validate) means an escape attempt reaches the human's eyes before being blocked — which is acceptable defence-in-depth: the human can deny it, and even if they approve, the validator still blocks it. Moving the validate check before the modal would require changes to GuardBot's approval logic, adding structural complexity for minimal gain.

**Alternative considered:** A `preflight` hook on `ToolDef` checked before `requires_approval`. Rejected: adds a second callable field and changes the guard/project bot approval flow; the current ordering is acceptable for the demo use case where escape attempts do not occur.

### D7 — `ValidationBlockEvent` in `commentator_bot.py`

**Decision:** `ValidationBlockEvent` is defined alongside `ToolCallEvent` in `commentator_bot.py`. `CommentatorBot.comment()` union type is extended; a new `_comment_on_validation_block()` method generates LLM colour commentary with a dim factual prefix.

**Rationale:** All commentary event types and their handlers live in one module. Adding `ValidationBlockEvent` there keeps the pattern consistent and avoids a separate events module.

## Risks / Trade-offs

**Shell false negatives** → Documented limitation. Paths embedded in quoted strings, `$()` subshells, or variable references are not caught. Mitigation: these require deliberate obfuscation; a well-prompted LLM won't produce them accidentally. The file tool validators are a safety net for operations that actually touch the filesystem.

**Approval modal shown for invalid shell calls** → Slightly awkward UX when a sandboxed `run_shell` call escapes: the human sees the modal for a call that will be blocked. Mitigation: this is defence-in-depth; the human can deny it at the modal, and the validator catches it anyway. In the demo context, escape attempts do not occur.

**`_make_bot` grows a new required parameter** → Any call site creating bots must provide `session_folder`. Mitigation: the only call sites are `make_bots()` (which already centralises bot creation) and tests; tests can pass `Path.cwd()` or a `tmp_path` fixture.

**`dataclasses.replace` on `ToolDef` copies all fields** → If `ToolDef` gains more fields in future, `replace` keeps working without changes. No risk.

## Migration Plan

No data migrations. The change is additive (`validate=None` by default) and internal. Steps:

1. Add `validate` field to `ToolDef` with `None` default — fully backward-compatible.
2. Add `dispatch_tool()` helper and `ValidationBlockEvent` — no existing behaviour changes.
3. Update the four bots' dispatch lines — one-line change each, covered by existing tests.
4. Wire `session_folder` through `make_bots()` / `_make_bot()` and apply validators.
5. Update `context.py` to accept and use `session_folder`.
6. Update `frontends/tui.py` to capture `Path.cwd()` and pass it through.

Rollback: revert the six changed files. No persistent state is introduced.

## Open Questions

None — all decisions were resolved during the design exploration session.
