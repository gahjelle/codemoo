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


async def _draft_gmail(to: str, subject: str, body: str) -> str:
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, headers=_get_headers(), json={"message": {"raw": raw}}
        )
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    draft_id = resp.json().get("id", "?")
    return f"Draft saved (id={draft_id}). Review it in your Gmail Drafts folder."


draft_gmail = ToolDef(
    name="draft_gmail",
    description=(
        "Save an email as a draft in Gmail. Returns a draft ID for use with send_gmail."
    ),
    parameters=[
        ToolParam(name="to", description="Recipient email address."),
        ToolParam(name="subject", description="Email subject line."),
        ToolParam(name="body", description="Plain-text email body."),
    ],
    fn=_draft_gmail,
    init=_init_workspace,
)


async def _send_gmail(draft_id: str) -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts/send"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=_get_headers(), json={"id": draft_id})
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    return "Email sent."


send_gmail = ToolDef(
    name="send_gmail",
    description="Send a previously drafted Gmail email by its draft ID.",
    parameters=[
        ToolParam(name="draft_id", description="Draft ID returned by draft_gmail."),
    ],
    fn=_send_gmail,
    requires_approval=True,
    init=_init_workspace,
)


async def _create_gcal_event(
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
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)
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


async def _post_chat_message(space_id: str, message: str) -> str:
    url = f"https://chat.googleapis.com/v1/spaces/{space_id}/messages"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=_get_headers(), json={"text": message})
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


async def _write_gdrive(filename: str, content: str, folder_id: str = "root") -> str:
    headers = _get_headers()
    search_url = "https://www.googleapis.com/drive/v3/files"
    search_params = {
        "q": f"name = '{filename}' and '{folder_id}' in parents and trashed = false",
        "fields": "files(id)",
        "pageSize": "1",
    }
    boundary = "codemoo_boundary_1234567890"
    upload_headers = {
        **headers,
        "Content-Type": f"multipart/related; boundary={boundary}",
    }
    async with httpx.AsyncClient() as client:
        search_resp = await client.get(
            search_url, headers=headers, params=search_params
        )
        if search_resp.is_error:
            return f"Error {search_resp.status_code}: {search_resp.text}"

        existing = search_resp.json().get("files", [])
        metadata = f'{{"name": "{filename}"}}'
        body = (
            f"--{boundary}\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{metadata}\r\n"
            f"--{boundary}\r\n"
            f"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
            f"{content}\r\n"
            f"--{boundary}--"
        )

        if existing:
            file_id = existing[0]["id"]
            upload_url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}"
            resp = await client.patch(
                upload_url,
                headers=upload_headers,
                params={"uploadType": "multipart"},
                content=body.encode(),
            )
            if resp.is_error:
                return f"Error {resp.status_code}: {resp.text}"
            return f"Updated {filename} ({file_id})"

        meta_with_parent = f'{{"name": "{filename}", "parents": ["{folder_id}"]}}'
        body = (
            f"--{boundary}\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{meta_with_parent}\r\n"
            f"--{boundary}\r\n"
            f"Content-Type: text/plain; charset=UTF-8\r\n\r\n"
            f"{content}\r\n"
            f"--{boundary}--"
        )
        upload_url = "https://www.googleapis.com/upload/drive/v3/files"
        resp = await client.post(
            upload_url,
            headers=upload_headers,
            params={"uploadType": "multipart"},
            content=body.encode(),
        )
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    file_id = resp.json().get("id", "?")
    return f"Created {filename} ({file_id})"


write_gdrive = ToolDef(
    name="write_gdrive",
    description=(
        "Create or update a plain text file in Google Drive."
        " If a file with the given name already exists in the folder,"
        " its content is replaced. Otherwise a new file is created."
    ),
    parameters=[
        ToolParam(name="filename", description="Name of the file to create or update."),
        ToolParam(name="content", description="Plain text content to write."),
        ToolParam(
            name="folder_id",
            description="Drive folder ID (default: root / My Drive).",
            required=False,
        ),
    ],
    fn=_write_gdrive,
    requires_approval=True,
    init=_init_workspace,
)
