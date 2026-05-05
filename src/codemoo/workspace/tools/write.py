"""Write/action Google Workspace tool definitions."""

import base64
from email.mime.text import MIMEText

import httpx

from codemoo.config import config
from codemoo.core.tools import ToolDef, ToolParam
from codemoo.workspace.auth import _init_workspace, get_credentials


def _get_headers() -> dict[str, str]:
    creds = get_credentials(config.workspace)
    return {"Authorization": f"Bearer {creds.token}"}


def _send_gmail(to: str, subject: str, body: str) -> str:
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    resp = httpx.post(url, headers=_get_headers(), json={"raw": raw})
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return f"Email sent to {to}"


send_gmail = ToolDef(
    name="send_gmail",
    description="Send an email via Gmail.",
    parameters=[
        ToolParam(name="to", description="Recipient email address."),
        ToolParam(name="subject", description="Email subject line."),
        ToolParam(name="body", description="Plain-text email body."),
    ],
    fn=_send_gmail,
    requires_approval=True,
    init=_init_workspace,
)


def _create_gcal_event(
    summary: str, start: str, end: str, description: str = ""
) -> str:
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    payload: dict[str, object] = {
        "summary": summary,
        "description": description,
    }
    if "T" in start:
        payload["start"] = {"dateTime": start, "timeZone": "UTC"}
        payload["end"] = {"dateTime": end, "timeZone": "UTC"}
    else:
        payload["start"] = {"date": start}
        payload["end"] = {"date": end}
    resp = httpx.post(url, headers=_get_headers(), json=payload)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    event = resp.json()
    event_id = event.get("id", "?")
    return f"Event created: {event.get('summary', summary)} (id={event_id})"


create_gcal_event = ToolDef(
    name="create_gcal_event",
    description="Create a Google Calendar event on the primary calendar.",
    parameters=[
        ToolParam(name="summary", description="Event title."),
        ToolParam(
            name="start",
            description="Start in ISO 8601 UTC format or YYYY-MM-DD for all-day.",
        ),
        ToolParam(
            name="end",
            description="End in ISO 8601 UTC format or YYYY-MM-DD for all-day.",
        ),
        ToolParam(
            name="description",
            description="Optional event description.",
            required=False,
        ),
    ],
    fn=_create_gcal_event,
    requires_approval=True,
    init=_init_workspace,
)


def _post_chat_message(space_id: str, message: str) -> str:
    url = f"https://chat.googleapis.com/v1/spaces/{space_id}/messages"
    resp = httpx.post(url, headers=_get_headers(), json={"text": message})
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return "Message posted to Google Chat space"


post_chat_message = ToolDef(
    name="post_chat_message",
    description="Post a plain-text message to a Google Chat space.",
    parameters=[
        ToolParam(name="space_id", description="The Google Chat space ID."),
        ToolParam(name="message", description="Message text to post."),
    ],
    fn=_post_chat_message,
    requires_approval=True,
    init=_init_workspace,
)
