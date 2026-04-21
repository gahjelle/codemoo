## 1. Extend build_llm_context

- [x] 1.1 Add optional `system: str = ""` parameter to `build_llm_context` in `src/codemoo/core/backend.py`
- [x] 1.2 When `system` is non-empty, prepend `Message(role="system", content=system)` as the first element
- [x] 1.3 Update tests in `tests/core/test_backend.py` to cover system message prepended when non-empty and absent when empty

## 2. Implement SystemBot

- [x] 2.1 Create `src/codemoo/core/bots/system_bot.py` with a `SystemBot` dataclass that has `name`, `emoji`, `backend`, `human_name`, `system`, and `max_messages` fields
- [x] 2.2 Implement `on_message` to call `build_llm_context` with `self.system` and return `ChatMessage(sender=self.name, text=response)`
- [x] 2.3 Export `SystemBot` from `src/codemoo/core/bots/__init__.py`

## 3. Tests for SystemBot

- [x] 3.1 Create `tests/core/bots/test_system_bot.py` covering: `is_human` is `False`, system message forwarded to context builder, history filtered to human + self, context clipped to `max_messages`, reply sender is `self.name`

## 4. Register Sigma

- [x] 4.1 Instantiate Sigma (name `"Sigma"`, emoji `"🎭"`) with a coding-agent system prompt in the bot registration code (wherever EchoBot/LLMBot/ChatBot are registered)
- [x] 4.2 Verify Sigma appears in the bot selection screen and responds distinctly from ChatBot (Iris) in a manual test
