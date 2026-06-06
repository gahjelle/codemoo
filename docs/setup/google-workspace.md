# Google Workspace Setup

Required for `workspace` mode.

## Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **New Project**
2. Enable the APIs you need: **Gmail API**, **Google Calendar API**, **Google Chat API**, **Google Drive API**
3. Go to **APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID**
4. Choose **Desktop app**, download the JSON, and note the `client_id` and `client_secret`
5. Go to **APIs & Services** → **OAuth consent screen** → **Add or remove scopes** and add the following sensitive scopes:

| Scope                | Used by                                  |
| -------------------- | ---------------------------------------- |
| `gmail.readonly`     | Read and list email                      |
| `gmail.compose`      | Create drafts and send drafts by ID      |
| `gmail.send`         | Send email directly                      |
| `calendar.readonly`  | Read calendar events                     |
| `calendar.events`    | Create calendar events                   |
| `drive`              | Read and write Drive files; post to Chat |

`gmail.compose` is required for the draft workflow — `gmail.send` alone only covers `POST .../messages/send` and does not authorize `POST .../drafts` or `POST .../drafts/{id}/send`.

If your project is in **Testing** mode, add any Google accounts that will use the app as test users under **OAuth consent screen** → **Test users**.

## Configure Codemoo

```console
export CODEMOO_WORKSPACE_CLIENT_ID=<your-client-id>
export CODEMOO_WORKSPACE_CLIENT_SECRET=<your-client-secret>
```

## Authenticate

The first time you run in `workspace` mode, Codemoo will print an authorization URL:

```plain
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
Enter the authorization code:
```

Open the URL, grant the requested permissions, and paste the authorization code back. The token is cached at `~/.cache/codemoo/workspace_token.pkl` so subsequent runs skip auth.

To re-authenticate, delete the token file.
