"""Google Workspace tool definitions."""

from codemoo.core.tools import ToolDef
from codemoo.workspace.tools.read import list_gcal, list_gmail, read_gmail
from codemoo.workspace.tools.write import (
    create_gcal_event,
    post_chat_message,
    send_gmail,
)

WORKSPACE_TOOL_REGISTRY: dict[str, ToolDef] = {
    t.name: t
    for t in [
        list_gmail,
        read_gmail,
        send_gmail,
        list_gcal,
        create_gcal_event,
        post_chat_message,
    ]
}
