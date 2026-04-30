"""Write/action Microsoft Graph tool definitions."""

import httpx

from codemoo.config import config
from codemoo.core.tools import ToolDef, ToolParam
from codemoo.m365.auth import _init_m365, get_access_token


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_access_token(config.m365, config.m365.scopes)}"
    }


def _send_email(to: str, subject: str, body: str) -> str:
    url = f"{config.m365.graph_base_url}/me/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}],
        }
    }
    resp = httpx.post(url, headers=_get_headers(), json=payload)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return f"Email sent to {to}"


send_email = ToolDef(
    name="send_email",
    description="Send an email via Microsoft Graph.",
    parameters=[
        ToolParam(name="to", description="Recipient email address."),
        ToolParam(name="subject", description="Email subject line."),
        ToolParam(name="body", description="Plain-text email body."),
    ],
    fn=_send_email,
    requires_approval=True,
    init=_init_m365,
)


def _create_calendar_event(subject: str, start: str, end: str, body: str = "") -> str:
    url = f"{config.m365.graph_base_url}/me/events"
    payload = {
        "subject": subject,
        "body": {"contentType": "Text", "content": body},
        "start": {"dateTime": start, "timeZone": "UTC"},
        "end": {"dateTime": end, "timeZone": "UTC"},
    }
    resp = httpx.post(url, headers=_get_headers(), json=payload)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    event = resp.json()
    event_id = event.get("id", "?")
    return f"Event created: {event.get('subject', subject)} (id={event_id})"


create_calendar_event = ToolDef(
    name="create_calendar_event",
    description="Create a calendar event via Microsoft Graph.",
    parameters=[
        ToolParam(name="subject", description="Event title."),
        ToolParam(name="start", description="Start datetime in ISO 8601 UTC format."),
        ToolParam(name="end", description="End datetime in ISO 8601 UTC format."),
        ToolParam(
            name="body",
            description="Optional event description.",
            required=False,
        ),
    ],
    fn=_create_calendar_event,
    requires_approval=True,
    init=_init_m365,
)


def _post_teams_message(team_id: str, channel_id: str, message: str) -> str:
    url = f"{config.m365.graph_base_url}/teams/{team_id}/channels/{channel_id}/messages"
    payload = {"body": {"content": message}}
    resp = httpx.post(url, headers=_get_headers(), json=payload)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return "Message posted to Teams channel"


post_teams_message = ToolDef(
    name="post_teams_message",
    description="Post a message to a Microsoft Teams channel.",
    parameters=[
        ToolParam(name="team_id", description="The Teams group/team ID."),
        ToolParam(name="channel_id", description="The channel ID within the team."),
        ToolParam(name="message", description="Message text to post."),
    ],
    fn=_post_teams_message,
    requires_approval=True,
    init=_init_m365,
)


def _write_sharepoint(site_path: str, item_path: str, content: str) -> str:
    host, path = site_path.split(":", 1) if ":" in site_path else (site_path, "/")
    base = config.m365.graph_base_url
    url = f"{base}/sites/{host}:{path}/drive/root:/{item_path}:/content"
    resp = httpx.put(
        url,
        headers={**_get_headers(), "Content-Type": "text/plain"},
        content=content.encode("utf-8"),
    )
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return f"Written {len(content)} characters to {item_path}"


write_sharepoint = ToolDef(
    name="write_sharepoint",
    description="Write text content to a SharePoint document (creates or overwrites).",
    parameters=[
        ToolParam(
            name="site_path",
            description="SharePoint site in host:/sites/name format.",
        ),
        ToolParam(
            name="item_path",
            description="Path to the file within the drive root.",
        ),
        ToolParam(name="content", description="Text content to write."),
    ],
    fn=_write_sharepoint,
    requires_approval=True,
    init=_init_m365,
)
