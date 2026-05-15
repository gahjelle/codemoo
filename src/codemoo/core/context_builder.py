"""Pure function that converts list[ContextItem] to list[Message]."""

import json

from codemoo.core.backend import Message, Role
from codemoo.core.context_items import (
    AssistantMessageContent,
    ContextItem,
    InjectedContent,
    ItemMode,
    SystemContent,
    ToolUseContent,
    UserMessageContent,
)


def build_context(items: list[ContextItem]) -> list[Message]:
    """Convert a list of ContextItems to LLM messages, applying mode and role rules."""
    messages: list[Message] = []
    for item in items:
        if item.mode == ItemMode.DISABLED:
            continue
        messages.extend(_to_messages(item))
    return messages


def _to_messages(item: ContextItem) -> list[Message]:
    content = item.content

    if isinstance(content, ToolUseContent):
        # role_override does not apply to tool pairs; EDITED/SUMMARY not supported
        return _tool_use_to_messages(content)

    text = _effective_text(item)
    role = _effective_role(item)
    return [Message(role=role, content=text)]


def _effective_text(item: ContextItem) -> str:
    if item.mode == ItemMode.SUMMARY and item.summary is not None:
        return item.summary
    if item.mode == ItemMode.EDITED and item.edited is not None:
        return item.edited
    content = item.content
    match content:
        case (
            UserMessageContent(text=t)
            | AssistantMessageContent(text=t)
            | SystemContent(text=t)
            | InjectedContent(text=t)
        ):
            return t
    return ""


def _effective_role(item: ContextItem) -> Role:
    if item.role_override is not None:
        return item.role_override
    content = item.content
    match content:
        case UserMessageContent():
            return "user"
        case AssistantMessageContent():
            return "assistant"
        case SystemContent():
            return "system"
        case InjectedContent(role=r):
            return r
    return "user"


def _tool_use_to_messages(content: ToolUseContent) -> list[Message]:
    return [
        Message(
            role="assistant",
            content="",
            tool_calls_json=json.dumps(
                [
                    {
                        "id": content.call_id,
                        "type": "function",
                        "function": {
                            "name": content.name,
                            "arguments": content.arguments_json,
                        },
                    }
                ]
            ),
        ),
        Message(
            role="tool",
            content=content.output,
            tool_call_id=content.call_id,
        ),
    ]
