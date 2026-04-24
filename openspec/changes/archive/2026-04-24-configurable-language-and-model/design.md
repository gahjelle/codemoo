## Context

The codebase has three places that use the LLM for "infrastructure" purposes (commentary, error formatting, demo slides). CommentatorBot hardcodes `"Answer in Norwegian"` in every persona prompt. ErrorBot and demo slides issue raw prompts with no language instruction, so they respond in the language the LLM chooses (usually English). The Mistral model is hardcoded as `"mistral-small-latest"` in `create_mistral_backend()`.

Changing either behaviour today requires editing source files, which is impractical for end-users and demo presenters who just want to run the app in a different language or against a different model tier.

## Goals / Non-Goals

**Goals:**
- Single env var `CODEMOO_LANGUAGE` injects a language instruction into CommentatorBot, ErrorBot, and demo slide prompts.
- Single env var `CODEMOO_MISTRAL_MODEL` overrides the default Mistral model in `create_mistral_backend()`.
- Participant bots remain untouched — they adapt naturally in-conversation.

**Non-Goals:**
- Per-bot language overrides.
- BCP 47 validation of the language value.
- UI for setting env vars at runtime.
- Supporting model names for backends other than Mistral.

## Decisions

### D1: Language instruction via env var, not a constructor parameter

**Decision**: Read `CODEMOO_LANGUAGE` at call-time (inside the prompt-building functions) rather than injecting it through constructors.

**Rationale**: CommentatorBot, ErrorBot, and SlideContent are constructed in different places (`tui.py`, `app.py`, `slides.py`). Threading a `language` parameter through all constructors would touch many call sites and create boilerplate. Env-var access at prompt-build time is simpler and keeps the interface stable.

**Alternative considered**: Pass `language: str | None` into constructors. Rejected — too much churn across unrelated call sites.

### D2: Helper function `_language_instruction()` in a shared config module

**Decision**: Add a small `src/codemoo/config.py` module with `language_instruction() -> str` that returns `" Answer in <LANG>."` when `CODEMOO_LANGUAGE` is set, or `""` when not set.

**Rationale**: Three files need the same logic. A single helper avoids duplicate `os.environ.get` calls, makes the behaviour easy to test, and gives a clear home for future env-var helpers.

**Alternative considered**: Inline `os.environ.get` in each file. Rejected — DRY violation, harder to test consistently.

### D3: Language clause appended to system prompts, not injected as a separate message

**Decision**: Append the language instruction as a suffix to the existing system prompt strings (or to the user-prompt string for demo slides, which don't use a system message).

**Rationale**: Keeps the persona character intact. A separate system message would compete with the persona prompt and may be ignored by some model configurations.

### D4: Model env var read in `create_mistral_backend()`, not globally

**Decision**: `create_mistral_backend()` reads `CODEMOO_MISTRAL_MODEL` as the default for its existing `model` parameter. Explicit callers who pass `model=` directly are unaffected.

**Rationale**: Minimal diff — only one line changes. The existing `model` parameter already provides override capability; the env var just sets the fallback.

## Risks / Trade-offs

- [Risk: Language instruction appended after persona character may produce inconsistent emphasis] → Mitigation: instruction is short and imperative (`"Answer in Norwegian."`); tested by inspection against existing personas.
- [Risk: Env var name conflicts with OS or other tools] → Mitigation: `CODEMOO_` prefix scopes the variables clearly.
- [Risk: `CODEMOO_MISTRAL_MODEL` set to an invalid model name causes runtime error] → Mitigation: Mistral API will return a clear error; no extra validation added per non-goals.

## Migration Plan

No data migration needed. Change is purely additive from the user perspective:
- Existing deployments without `CODEMOO_LANGUAGE` behave the same as today (no language instruction for ErrorBot/slides, Norwegian removed from CommentatorBot — see note below).
- Deployments that previously relied on the hardcoded Norwegian in CommentatorBot MUST set `CODEMOO_LANGUAGE=Norwegian` to preserve behaviour.

## Open Questions

None.
