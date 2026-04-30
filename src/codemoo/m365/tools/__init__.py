"""Microsoft Graph tool definitions."""

from codemoo.core.tools import ToolDef
from codemoo.m365.tools.read import (
    list_calendar,
    list_email,
    list_sharepoint,
    read_email,
    read_sharepoint,
)
from codemoo.m365.tools.write import (
    create_calendar_event,
    post_teams_message,
    send_email,
    write_sharepoint,
)

M365_TOOL_REGISTRY: dict[str, ToolDef] = {
    t.name: t
    for t in [
        list_sharepoint,
        read_sharepoint,
        list_email,
        read_email,
        list_calendar,
        send_email,
        create_calendar_event,
        post_teams_message,
        write_sharepoint,
    ]
}
