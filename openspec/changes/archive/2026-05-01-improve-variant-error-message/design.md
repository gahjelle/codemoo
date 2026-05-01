## Context

`resolve()` in `src/codemoo/config/schema.py` converts a `BotRef` (type + variant string) into a `ResolvedBotConfig` by looking up the variant in `BotConfig.variants`. When the variant key is absent, Python raises a bare `KeyError` whose `str()` representation is just the quoted key — e.g. `'bad'`. This surfaces verbatim in the CLI error panel because `code_chat` / `business_chat` catch all exceptions and display `str(err)`.

Variant names have no Literal type and no tab-completion — they are free-form strings validated only at resolution time.

## Goals / Non-Goals

**Goals:**
- `resolve()` raises `ValueError` with a message that names the bot type, the unknown variant, and lists all valid variants sorted alphabetically.

**Non-Goals:**
- Variant validation at the CLI/argument-parsing layer.
- Typing variants as a closed Literal.
- Changing the error for an unknown bot type (already handled by cyclopts).

## Decisions

### Raise `ValueError`, not `KeyError`

`KeyError` is an implementation detail of the dict lookup; `ValueError` is the idiomatic Python signal for "argument has the right type but an invalid value." The existing `except Exception` catcher in the CLI layer handles either, so the change is purely semantic — but it also aligns with how Pydantic validators signal bad values in this codebase.

**Alternative considered:** A custom `UnknownVariantError(ValueError)` — adds no value for a one-off diagnostic; plain `ValueError` is sufficient.

### Sort variants alphabetically in the message

Alphabetical order is deterministic and makes the message testable without caring about dict insertion order. The user scans for the name they want, not the order they were defined.

### Fix at `resolve()`, not at the call sites

`resolve()` is the single point where a `BotRef` is materialised against the config. Fixing it here means every caller (CLI, demo runner, selection screen) gets the improved message for free.

### Change `resolve_backend()` to raise `ValueError`, then narrow the TUI `except`

`resolve_backend()` currently raises `RuntimeError` when all configured backends are exhausted. `RuntimeError` typically signals something genuinely unexpected — a programming error or an unrecoverable state the code didn't anticipate. "You configured no working backends" is squarely a value/configuration problem, so `ValueError` is more semantically accurate.

With that change, every pre-flight error the CLI needs to surface (`resolve()` bad variant, `resolve_backend()` no backends, `resolve_bot()` unknown spec) is a `ValueError`. The `except Exception` clauses in `code_chat()` and `business_chat()` can be narrowed to `except ValueError`, which removes the `# noqa: BLE001` suppressions and makes the intent explicit: these two entry points handle exactly the known configuration failure modes.

The demo commands (`code_demo`, `business_demo`) already use `except ValueError` — this brings the direct-chat commands in line with that existing pattern.

**Alternative considered:** Catch `(ValueError, RuntimeError)` in the TUI and leave `factory.py` unchanged. Rejected because `RuntimeError` has a different semantic weight and the union catch still reads as "we expected both of these," which is misleading.

## Risks / Trade-offs

- [Existing test] Any test that asserts `resolve()` raises `KeyError` for an unknown variant will need to be updated to `ValueError`. → Covered in tasks.
- [Unexpected exceptions] Narrowing from `except Exception` means a genuine unexpected exception (e.g., a bug in backend init) will now surface as a traceback rather than the error panel. This is the correct behaviour — the panel is for expected failures, not bugs.
