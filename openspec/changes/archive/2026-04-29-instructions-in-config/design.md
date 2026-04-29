## Context

Bot instructions (system prompts) are currently hardcoded as `_INSTRUCTIONS` module-level constants in each bot Python file. `ResolvedBotConfig` already carries all other variant-specific state (`description`, `tools`, `prompts`). The `_make_bot` factory in `__init__.py` dispatches on bot type and already constructs every bot from config-resolved values. `SingleTurnToolBot.instructions: str` already has no default at the base class; subclasses only re-declare it with `= _INSTRUCTIONS` as a convenience default. The infrastructure is ready — instructions just need to flow through config like tools already do.

## Goals / Non-Goals

**Goals:**
- `BotVariantConfig.instructions` and `ResolvedBotConfig.instructions` carry instructions per variant
- `_make_bot` passes resolved instructions to the 8 bots that accept them
- `_INSTRUCTIONS` constants removed from all bot files; instructions become required with no default on `SystemBot`, `AgentBot`, `GuardBot`, and the `SingleTurnToolBot` subclasses
- `codemoo.toml` supplies distinct instructions per variant (key fix: `AgentBot.code` ≠ `AgentBot.m365`, `GuardBot.code` ≠ `GuardBot.m365`)
- Demo slide comparison injects instructions into the LLM prompt (mirrors existing tools injection)

**Non-Goals:**
- Changing how instructions reach the LLM (`build_llm_context(system=...)` unchanged)
- Dynamic or templated instruction strings
- Adding new bot types or changing class hierarchy
- Resolving the `system` vs `instructions` field-name discrepancy in the `system-bot` spec

## Decisions

### `instructions` lives on `BotVariantConfig`, not `BotConfig`

Instructions are variant-specific by design — the entire motivation is that `AgentBot.code` and `AgentBot.m365` need different text. Placing them on `BotVariantConfig` (alongside `tools` and `prompts`) is consistent and avoids a separate override mechanism.

Default value is `""` so that `EchoBot`, `LlmBot`, and `ChatBot` — which have no instructions field on their dataclasses — do not require a dummy config entry.

**Alternative considered:** A top-level `instructions` on `BotConfig` with per-variant overrides. Rejected: more complex schema, still requires every variant to opt in, no cleaner than just putting it on the variant.

### Remove `_INSTRUCTIONS` entirely (Option A)

All `_INSTRUCTIONS` constants are deleted. Bot classes that accept `instructions` declare `instructions: str` with no default, making it a required constructor argument. `_make_bot` always passes `resolved.instructions`, so production code never hits a missing value. Tests that construct bots directly must supply explicit strings — this is intentional; it prevents stale defaults from silently passing tests.

**Alternative considered:** Keep `_INSTRUCTIONS` as generic stubs. Rejected: the stubs would drift from config values and could mask misconfiguration in tests.

### `_make_bot` is the only injection site

The match statement in `_make_bot` already knows the concrete type being constructed. Adding `instructions=resolved.instructions` to the 8 relevant cases is the minimal, explicit change. No reflection, no protocol check, no shared base class needed. `EchoBot`, `LlmBot`, and `ChatBot` branches receive no change.

### Slide prompt injection mirrors the tools pattern

`_build_llm_prompt` already appends:
```python
curr_tools_line = f"\n{current_bot.name} tools: {curr_tools}" if curr_tools else ""
```
Instructions follow the same pattern using `current_resolved.instructions` (already available as `ResolvedBotConfig`). When instructions are empty the line is omitted — the same guard as tools.

## Risks / Trade-offs

**Constructor breakage in tests** → Every test that constructs a bot class with an `instructions` field must be updated to pass an explicit string. The type checker and the test suite both catch this; it is mechanical work, not a design risk.

**Config omission causes a hard crash** → If a bot variant in TOML is missing `instructions`, `_make_bot` passes `""` (the `BotVariantConfig` default), which is a valid empty string — not a crash. `SystemBot` with empty instructions silently becomes equivalent to `ChatBot`. Mitigation: the task list ensures every relevant variant gets populated; existing demo tests will surface the regression.

**Slide LLM quality for `SystemBot`** → Moving instructions out of source code means the slide LLM no longer reads the persona text embedded in a string literal. With explicit injection it sees the text directly in the prompt, which is equally clear — likely clearer, since it's labeled.

## Migration Plan

No live system or database. All changes land in a single PR:

1. Extend schema (`BotVariantConfig`, `ResolvedBotConfig`, `resolve`)
2. Update `_make_bot` to pass instructions
3. Remove `_INSTRUCTIONS` from all bot files; remove re-declarations; make field required where applicable
4. Populate `codemoo.toml` with instructions for every affected variant
5. Update slide comparison prompt builder
6. Update tests

Rollback: revert the PR. No config migration, no persistent state affected.

## Open Questions

None — all decisions were resolved during the explore phase.
