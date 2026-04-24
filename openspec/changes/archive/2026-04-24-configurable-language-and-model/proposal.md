## Why

CommentatorBot hardcodes Norwegian in its prompts, while ErrorBot and demo slides have no language instruction at all — making the app's language behaviour inconsistent and impossible to change without editing source code. The Mistral model name is similarly baked in, requiring a code change to switch between small and large models.

## What Changes

- Add `CODEMOO_LANGUAGE` environment variable that injects a language instruction into CommentatorBot, ErrorBot, and demo slide prompts.
- Remove the hardcoded `"Answer in Norwegian"` strings from CommentatorBot; replace with the env-var-driven instruction.
- ErrorBot personas gain a language instruction when the env var is set.
- Demo slide LLM prompt gains a language instruction when the env var is set.
- Add `CODEMOO_MISTRAL_MODEL` environment variable; `create_mistral_backend()` reads it instead of defaulting to `"mistral-small-latest"` unconditionally.
- Participant bots (EchoBot, LLMBot, AgentBot, etc.) are unaffected — they adapt naturally to the user's language in conversation.

## Capabilities

### New Capabilities

- `env-language-config`: Language instruction injected into CommentatorBot, ErrorBot, and demo slide prompts via `CODEMOO_LANGUAGE`; unset means no language instruction.
- `env-model-config`: Mistral model name read from `CODEMOO_MISTRAL_MODEL` env var, falling back to `"mistral-small-latest"`.

### Modified Capabilities

- `commentator-bot`: Language instruction clause removed from hardcoded prompts; now derived from env var.
- `error-bot`: System prompts gain an optional language clause when `CODEMOO_LANGUAGE` is set.
- `llm-backend`: `create_mistral_backend()` reads `CODEMOO_MISTRAL_MODEL` for the default model name.

## Non-goals

- Supporting per-bot language overrides beyond the single env var.
- Validating that the language value is a real BCP 47 tag.
- Changing how participant bots handle language (they already adapt in-conversation).
- Adding a UI settings panel for these options.

## Impact

- `src/codemoo/core/bots/commentator_bot.py` — remove hardcoded Norwegian strings.
- `src/codemoo/core/bots/error_bot.py` — append language instruction to persona prompts.
- `src/codemoo/chat/slides.py` — append language instruction to LLM prompt strings.
- `src/codemoo/llm/backend.py` — read `CODEMOO_MISTRAL_MODEL` in `create_mistral_backend()`.
- Tests for backend, commentator, and error bot updated accordingly.
