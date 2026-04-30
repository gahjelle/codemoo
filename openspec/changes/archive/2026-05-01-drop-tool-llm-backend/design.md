## Context

`core/backend.py` currently defines two protocols: `LLMBackend` and `ToolLLMBackend`. `ToolLLMBackend` was created to mark backends that fully support tool calling, expecting it would carry additional methods or constraints. The two protocols have converged to identical `complete()` signatures, making `ToolLLMBackend` a redundant alias with zero semantic value.

Ten source files import `ToolLLMBackend`: the three concrete LLM backends (`anthropic.py`, `mistral.py`, `openrouter.py`), the factory (`factory.py`), the TUI frontend, and five bot classes.

## Goals / Non-Goals

**Goals:**
- Remove `ToolLLMBackend` from `core/backend.py`
- Replace every `ToolLLMBackend` annotation in the codebase with `LLMBackend`
- Update the `llm-backend` spec to remove the `ToolLLMBackend` requirement

**Non-Goals:**
- Any change to runtime behavior or method signatures
- Changing the overload structure on `LLMBackend.complete()`

## Decisions

**Replace with `LLMBackend`, not a new type.**
Since the signatures are identical, `LLMBackend` already expresses all necessary constraints. No intermediate type is needed.

**Update the spec as part of this change.**
The `llm-backend` spec currently includes a `ToolLLMBackend` requirement. Leaving it in place would create a drift between spec and code; the spec must be updated alongside the code.

## Risks / Trade-offs

- **Minimal risk** — this is a pure rename with no behavior change. All protocol satisfaction checks pass unchanged since `LLMBackend` and `ToolLLMBackend` had identical signatures.
- **No migration needed** — no external consumers; all usages are within this repo.
