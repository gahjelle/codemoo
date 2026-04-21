## Context

The project builds bots step by step, each adding exactly one capability. ChatBot (Iris) has conversation history but no persona. SystemBot (Sigma) is the next step: same LLM, same history, but now the LLM receives a system prompt that fixes its role and behavior. The demo talking point is "same LLM, totally different character."

`build_llm_context` in `core/backend.py` currently produces a flat list of user/assistant messages with no system role. All existing bots rely on this function unchanged.

## Goals / Non-Goals

**Goals:**
- `SystemBot` accepts a `system: str` field and prepends it as a `system` role message
- `build_llm_context` gains an optional `system` parameter so the logic stays in one place
- Sigma ships with a hard-coded coding-agent persona that is unmistakably different from default ChatBot behavior
- Existing bots (`LLMBot`, `ChatBot`) require zero changes to keep working

**Non-Goals:**
- UI for editing the system prompt at runtime
- Per-session or per-user system prompt configuration
- Anything beyond a single static system prompt per bot instance

## Decisions

### Extend `build_llm_context` rather than prepend in `SystemBot.on_message`

The context-building logic already lives in `build_llm_context`. Adding an optional `system: str = ""` parameter keeps system-prompt insertion in the pure functional core alongside all other context-shaping logic. `SystemBot.on_message` passes `self.system` through; calling code that omits it gets the old behavior unchanged.

Alternative considered: prepend in `SystemBot.on_message` after calling `build_llm_context`. Rejected because it splits context-assembly across two places and makes testing harder.

### `SystemBot` composes `ChatBot` behavior via field delegation, not inheritance

`SystemBot` is a dataclass that holds a `backend`, `human_name`, and `max_messages` just like `ChatBot`, and calls `build_llm_context` directly. It does not subclass `ChatBot`.

Alternative: subclass `ChatBot` and override `on_message`. Rejected because dataclass inheritance is awkward and the demo value comes from showing a clearly distinct, self-contained class — the audience should see it as a new bot, not a patched version.

### Coding-agent persona: opinionated, code-first, refusals for non-coding

Sigma's system prompt instructs the LLM to: respond only in code and terse prose, refuse off-topic requests with a one-liner, always prefer the simplest correct solution, and never add unsolicited pleasantries. This makes the difference obvious in a live demo even with short exchanges.

## Risks / Trade-offs

- [System prompt token cost] Each call now includes extra tokens → Mitigation: system prompts are short (< 200 tokens); negligible.
- [Persona bleed with long histories] After many turns the persona can weaken → Mitigation: out of scope; `max_messages` already clips history.
- [Test coverage of persona content] The actual wording of the system prompt is not tested, only its presence → Mitigation: the spec requires the system message appears first; wording is a design choice reviewable in code.
