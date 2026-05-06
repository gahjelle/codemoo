"""Google Workspace tool definitions."""

from codemoo.core.tools import ToolDef
from codemoo.workspace.tools.read import (
    list_gcal,
    list_gdrive,
    list_gmail,
    read_gdrive,
    read_gmail,
)
from codemoo.workspace.tools.write import (
    create_gcal_event,
    post_chat_message,
    send_gmail,
    write_gdrive,
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
        list_gdrive,
        read_gdrive,
        write_gdrive,
    ]
}
