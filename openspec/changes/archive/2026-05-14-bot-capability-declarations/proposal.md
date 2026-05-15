## Why

Bots are currently defined by their class and config, but the chat UI is static regardless of which bot is active. As bots gain richer capabilities (memory, context, tool management), the environment should be able to surface matching UI — without the bot knowing anything about the UI layer.

## What Changes

- Add a `capabilities` field to `BotVariantConfig` (and propagate to `ResolvedBotConfig`) using a `BotCapability` Literal type, starting with `"context_management"`
- Add `capabilities = ["context_management"]` to all three RetryBot variants in `codemoo.toml`
- Wire a dispatch table into `ChatApp` that activates capability-specific UI based on the active bot's declared capabilities
- Implement `context_management` as a PoC: a status bar below `ThinkingStatus` showing `Num messages: N`, updated after each reply batch

## Non-goals

- Implementing `tool_management` or any other capability beyond `context_management`
- Changing the `ChatParticipant` protocol — bots remain unaware of the UI
- Dynamic capability changes mid-session (capabilities are fixed at startup from config)

## Capabilities

### New Capabilities

- `bot-capability-declarations`: Config field and schema type for declaring which environment capabilities a bot requires; dispatch table in `ChatApp` that activates registered UI features per capability

### Modified Capabilities

- `bot-variant-config`: Adds a `capabilities` field to the variant config schema
- `chat-ui`: Adds a capability dispatch table and the `context_management` PoC status bar

## Impact

- `src/codemoo/config/schema.py` — new `BotCapability` Literal type, new field on `BotVariantConfig`, new field on `ResolvedBotConfig`, updated `resolve()`
- `src/codemoo/config/codemoo.toml` — `capabilities` added to RetryBot variants
- `src/codemoo/chat/app.py` — capability dispatch table, `_active_capabilities` set, hook to update context status after dispatch
- `src/codemoo/chat/context_status.py` — new widget (new file)
- `src/codemoo/chat/chat.tcss` — styles for `ContextStatus`
