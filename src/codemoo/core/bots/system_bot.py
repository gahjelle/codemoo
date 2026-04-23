"""Context-aware LLM bot with a fixed system prompt."""

import dataclasses
from typing import ClassVar

from codemoo.core.backend import LLMBackend, build_llm_context
from codemoo.core.message import ChatMessage

_INSTRUCTIONS = """
You are Sona, a ruthlessly practical coding assistant.
Rules you never break:
(1) Respond only about code and software engineering — for anything else reply
    with exactly 'Not my domain.' and nothing more.
(2) Never use pleasantries, filler, or preamble — get straight to the answer.
(3) Prefer the simplest correct solution; do not over-engineer.
(4) When showing code, show only the relevant snippet, not the whole file.
(5) If a question is ambiguous, state your assumption in one line then answer it.
""".strip()


@dataclasses.dataclass(eq=False)
class SystemBot:
    """Chat participant that injects a system prompt into every LLM context.

    Identical to ChatBot except that it prepends a fixed system-role message,
    giving the LLM a persona or behavioral instructions it cannot override.
    """

    name: str
    emoji: str
    backend: LLMBackend
    human_name: str
    instructions: str = _INSTRUCTIONS
    max_messages: int = 20
    is_human: ClassVar[bool] = False

    async def on_message(
        self, message: ChatMessage, history: list[ChatMessage]
    ) -> ChatMessage | None:
        """Respond using filtered conversation history prefixed by the system prompt."""
        context = build_llm_context(
            history,
            message,
            bot_name=self.name,
            human_name=self.human_name,
            max_messages=self.max_messages,
            system=self.instructions,
        )
        response = await self.backend.complete(context)
        return ChatMessage(sender=self.name, text=response)
