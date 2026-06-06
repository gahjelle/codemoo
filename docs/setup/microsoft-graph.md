# Microsoft Graph Setup

Required for `m365` mode.

## Register an Entra App

1. Go to [portal.azure.com](https://portal.azure.com) → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Name it (e.g. `Codemoo Demo`), leave supported account types as **single tenant**, and click **Register**
3. On the app overview page, copy the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Authentication** → **Add a platform** → **Mobile and desktop applications** → tick the `https://login.microsoftonline.com/common/oauth2/nativeclient` redirect URI → **Configure**
5. Under **Advanced settings** on the same page, set **Allow public client flows** to **Yes** → **Save**

The redirect URI and public client flag enable the device code flow Codemoo uses — no client secret is needed.

## Grant API Permissions

Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions** and add:

| Permission            | Consent required | Used by                                              |
| --------------------- | ---------------- | ---------------------------------------------------- |
| `Mail.ReadWrite`      | User             | Read email; create and manage drafts                 |
| `Mail.Send`           | User             | Send email (including sending a draft by ID)         |
| `Calendars.ReadWrite` | User             | Read and create calendar events                      |
| `Sites.Read.All`      | **Admin**        | Read SharePoint documents                            |
| `Files.ReadWrite.All` | **Admin**        | Write SharePoint documents                           |
| `ChannelMessage.Send` | **Admin**        | Post Teams messages                                  |

`Mail.ReadWrite` (not just `Mail.Read`) is required because drafts are created via `POST /me/messages`, which is a write operation.

For the `m365_lite` script only `Mail.ReadWrite`, `Mail.Send`, and `Calendars.ReadWrite` are needed — no admin consent required.

After adding permissions, click **Grant admin consent for \<tenant\>** if you have admin rights, or ask your tenant admin to do so for the admin-only permissions.

## Configure Codemoo

```console
export CODEMOO_M365_TENANT_ID=<your-tenant-id>
export CODEMOO_M365_CLIENT_ID=<your-client-id>
export CODEMOO_M365_SHAREPOINT_HOST=<your-tenant>.sharepoint.com
export CODEMOO_M365_SHAREPOINT_SITE=/sites/<your-site>
```

## Authenticate

The first time you run in `m365` mode, Codemoo will print a device code and a URL:

```plain
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code ABCD1234 to authenticate.
```

Open the URL, enter the code, and sign in with your Microsoft account. The token is cached at `~/.cache/codemoo/token_cache.bin` so subsequent runs are silent for up to 90 days.
