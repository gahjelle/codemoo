## REMOVED Requirements

### Requirement: build_llm_context is a pure function that produces a Message list
**Reason**: `build_llm_context` is deleted. Each bot now builds its `list[Message]` inline.
**Migration**: Inline context construction directly in `on_message`. Use `[*[Message(...) for m in history], Message(role="user", content=message.text)]`, prepending `Message(role="system", content=instructions)` if the bot has a system prompt.

### Requirement: build_llm_context filters history to relevant senders
**Reason**: Filtering is removed as part of this change. All history messages are included; the calling bot's own messages map to "assistant", all others to "user".
**Migration**: No replacement. Reintroduce filtering explicitly if needed in future.

### Requirement: build_llm_context maps senders to LLM roles
**Reason**: Role mapping is now inlined in each bot using `"assistant" if m.sender == self.name else "user"`.
**Migration**: See inline pattern above.

### Requirement: build_llm_context clips filtered history to max_messages
**Reason**: Clipping is removed. No context-length guard is applied.
**Migration**: No replacement. Add a dedicated context-management layer if needed in future.

### Requirement: build_llm_context prepends a system message when system is non-empty
**Reason**: System message prepending is now inlined in each bot that has instructions.
**Migration**: Prepend `Message(role="system", content=self.instructions)` as the first list element.
