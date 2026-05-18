"""Token count estimation using tiktoken cl100k_base encoder."""

import tiktoken

from codemoo.core.backend import Message

_enc = tiktoken.get_encoding("cl100k_base")


def estimate_tokens(messages: list[Message]) -> int:
    """Estimate total token count from a list of LLM messages.

    Uses cl100k_base (GPT-4's encoder) as an approximation; accurate to within
    ~5-10% for Claude and most other models. The ~ prefix in UI output signals
    this is an estimate.
    """
    total = 0
    for msg in messages:
        total += len(_enc.encode(msg.content or ""))
        if msg.tool_calls_json is not None:
            total += len(_enc.encode(msg.tool_calls_json))
    return total
