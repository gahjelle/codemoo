# Codemoo - Demonstrate how coding agents work under the hood

Requirements:

- `uv`
- An API key for at least one LLM provider (Mistral, OpenAI, Google, OpenRouter, or Anthropic), or a running [Ollama](https://ollama.com) server for local use
- Microsoft Graph access is required for `m365` mode
- Google Workspace OAuth credentials are required for `workspace` mode

## Installation

You should install Codemoo as a tool:

```console
uv tool install . --editable
```

> **Important:** Some of the demo bots can run destructable commands without any confirmation. Be careful with your prompts!

## Configuration

Codemoo can run in several modes:

- **`code`** is the default mode where it is your friendly coding assistant (similar to Claude Code, OpenCode, Codex, and GitHub Copilot).
- **`m365`** requires access to [Microsoft Graph](#microsoft-graph) and gives Codemoo access to your Outlook email, Teams, Calendar, and SharePoint — similar to M365 Copilot.
- **`workspace`** requires [Google Workspace](#google-workspace) OAuth credentials and gives Codemoo access to Gmail, Google Calendar, and Google Chat.

**General Setup**

| Variable           | Default   | Description                                                          |
| ------------------ | --------- | -------------------------------------------------------------------- |
| `CODEMOO_LANGUAGE` | `English` | Language for commentary, error messages, and demo slides and prompts |

**LLM Backends**

Codemoo will try all different LLM backends until it finds one that is set up. If you want to explicitly choose one backend, use the following environment variable:
The priority order of the different backends is: `mistral` → `ollama` → `openrouter` → `google` → `anthropic` → `openai`.

| Variable          | Default   | Description                                                                           |
| ----------------- | --------- | ------------------------------------------------------------------------------------- |
| `CODEMOO_BACKEND` | `mistral` | Active backend: `mistral`, `ollama`, `openrouter`, `google`, `anthropic`, or `openai` |

To set up an LLM backend, you need to provide an API key in an environment variable. You can optionally override which model is being used. Codemoo will show the active backend and model in the lower right corner of the screen.

| Variable                   | Default                     | Description                                                                       |
| -------------------------- | --------------------------- | --------------------------------------------------------------------------------- |
| `MISTRAL_API_KEY`          | —                           | Mistral API key (required for mistral backend)                                    |
| `CODEMOO_MISTRAL_MODEL`    | `mistral-small-latest`      | Mistral model override                                                            |
| `OLLAMA_API_KEY`           | `ollama`                    | Ollama API key (optional; defaults to `ollama` for unauthenticated local servers) |
| `CODEMOO_OLLAMA_MODEL`     | `qwen2.5-coder:7b`          | Ollama model override                                                             |
| `OPENROUTER_API_KEY`       | —                           | OpenRouter API key (required for openrouter backend)                              |
| `CODEMOO_OPENROUTER_MODEL` | `z-ai/glm-4.5-air:free`     | OpenRouter model override                                                         |
| `GOOGLE_API_KEY`           | —                           | Google AI API key (required for google backend)                                   |
| `CODEMOO_GOOGLE_MODEL`     | `gemini-2.0-flash`          | Google model override                                                             |
| `ANTHROPIC_API_KEY`        | —                           | Anthropic API key (required for anthropic backend)                                |
| `CODEMOO_ANTHROPIC_MODEL`  | `claude-haiku-4-5-20251001` | Anthropic model override                                                          |
| `OPENAI_API_KEY`           | —                           | OpenAI API key (required for openai backend)                                      |
| `CODEMOO_OPENAI_MODEL`     | `gpt-4o-mini`               | OpenAI model override                                                             |


For local Ollama usage, install [Ollama](https://ollama.com), pull a model (`ollama pull qwen2.5-coder:7b`), and set `CODEMOO_BACKEND=ollama`. No API key is required. The `base_url` for each provider can also be overridden in a local `codemoo.toml` — useful for pointing the `openai` backend at Azure AI Foundry or other compatible endpoints.

**Microsoft Graph**

| Variable                  | Default                  | Description                 |
| ------------------------- | ------------------------ | --------------------------- |
| `CODEMOO_M365_TENANT_ID`  | —                        | Microsoft Graph tenant ID   |
| `CODEMOO_M365_CLIENT_ID`  | —                        | Microsoft Graph client ID   |
| `CODEMOO_SHAREPOINT_HOST` | `contoso.sharepoint.com` | Base URL to Sharepoint      |
| `CODEMOO_SHAREPOINT_SITE` | `/sites/demo`            | Site link inside Sharepoint |


## Usage

Codemoo has two main modes: a coding assistant you can use directly, and a step-by-step demo that shows how coding agents work under the hood.

### Coding assistant

Launch the chat with the most capable bot:

```console
uv run codemoo
```

The business chat is named Collebra, and can be run in the same way as Codemoo (requires an Entra app registration and correctly set [environment variables](#configuration).):

```console
uv run collebra
uv run codemoo --variant m365
```

Use `--bot` to start with a specific bot by type:

```console
uv run codemoo --bot ReadBot
```

To pick a bot interactively before starting:

```console
uv run codemoo select
```

To see all available bots:

```console
uv run codemoo list-bots
```

### Demo mode

Run through the bot progression to see how coding agents evolve step by step — from a simple echo bot up to a full agent loop.

> **Note:** The example prompts for later bots reference files in the `demo/` folder. Run the demo from there so the paths resolve correctly:
>
> ```console
> cd demo
> ```

Start the interactive demo by running Codemoo with the `demo` command:

```console
uv run codemoo demo
```

Each bot is introduced with slides explaining what it can do and how it works. Press **Ctrl-N** to advance to the next bot, or **Ctrl-Q** to quit. Press **Ctrl-S** at any point to reopen the current bot's slide. Each bot also comes with a few example prompts. Press **Ctrl-E** to insert the next example prompt. You can then edit it or just press enter to submit it directly.

You can also start or end the demo with specific bots:

```console
uv run codemoo demo --start telo --end loom
```

For different demo purposes, you can run with different preset scripts (lists of bots):

```console
uv run codemoo list-scripts
uv run codemoo demo --script focused
```

Scripts can also be further customized by providing `--start` and `--end`.

### Language support

You can set language with `CODEMOO_LANGUAGE`. For example, if you use `CODEMOO_LANGUAGE=Norwegian` then demo slides and prompts, as well as commentary and error messages will be translated to Norwegian (or your chosen language).

## Bot progression

**Coding path** (`--script default`):

| #   | Bot        | Capability                                         |
| --- | ---------- | -------------------------------------------------- |
| 1   | 🦜 Coco     | Echo — repeats your message back                   |
| 2   | ✨ Mono     | LLM — single-turn language model call              |
| 3   | 🧿 Iris     | Chat — multi-turn conversation with history        |
| 4   | 🎭 Sona     | System prompt — chat with a persona                |
| 5   | 🔧 Telo     | Tools — can call a tool and act on the result      |
| 6   | 📁 **Rune** | ReadBot — reads files and lists directories        |
| 7   | 🔨 **Axel** | ChangeBot — runs shell commands and writes files   |
| 8   | 🌀 Loom     | Agent — full agentic loop with planning            |
| 9   | 🔒 Cato     | Guard — human-in-the-loop before risky actions     |
| 10  | Lore 📖     | Project context - inject information in every call |

**M365 path** (`--script m365`):

| #   | Bot        | Capability                                                    |
| --- | ---------- | ------------------------------------------------------------- |
| 1   | 🦜 Coco     | Echo — repeats your message back                              |
| 2   | ✨ Mono     | LLM — single-turn language model call                         |
| 3   | 🧿 Iris     | Chat — multi-turn conversation with history                   |
| 4   | 🎭 Sona     | System prompt — chat with a persona                           |
| 5   | 🔧 Telo     | Tools — can call a tool and act on the result                 |
| 6   | 🚶 **Roam** | ScanBot — reads SharePoint, Outlook email, and calendar       |
| 7   | 📤 **Aero** | SendBot — sends Outlook email, creates events, posts to Teams |
| 8   | 🌀 Loom     | Agent — full agentic loop over M365 data                      |
| 9   | 🔒 Cato     | Guard — human approval before M365 actions                    |
| 10  | Lore 📖     | Project context - inject information in every call            |

**Workspace path** (`--script workspace`):

| #   | Bot        | Capability                                                    |
| --- | ---------- | ------------------------------------------------------------- |
| 1   | 🦜 Coco     | Echo — repeats your message back                              |
| 2   | ✨ Mono     | LLM — single-turn language model call                         |
| 3   | 🧿 Iris     | Chat — multi-turn conversation with history                   |
| 4   | 🎭 Sona     | System prompt — chat with a persona                           |
| 5   | 🔧 Telo     | Tools — can call a tool and act on the result                 |
| 6   | 🚶 **Roam** | ScanBot — reads Gmail and Google Calendar                     |
| 7   | 📤 **Aero** | SendBot — sends Gmail, creates Calendar events, posts to Chat |
| 8   | 🌀 Loom     | Agent — full agentic loop over Google Workspace data          |
| 9   | 🔒 Cato     | Guard — human approval before Workspace actions               |
| 10  | Lore 📖     | Project context - inject information in every call            |

See [BOTS.md](BOTS.md) for more information about the bots.

## Microsoft Graph

If you run in `m365` mode, you need to set up access to your Microsoft Graph tenant.

### Register an Entra app

1. Go to [portal.azure.com](https://portal.azure.com) → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Name it (e.g. `Codemoo Demo`), leave supported account types as **single tenant**, and click **Register**
3. On the app overview page, copy the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **Authentication** → **Add a platform** → **Mobile and desktop applications** → tick the `https://login.microsoftonline.com/common/oauth2/nativeclient` redirect URI → **Configure**
5. Under **Advanced settings** on the same page, set **Allow public client flows** to **Yes** → **Save**

The redirect URI and public client flag enable the device code flow Codemoo uses — no client secret is needed.

### Grant API permissions

Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions** and add:

| Permission            | Consent required | Used by                         |
| --------------------- | ---------------- | ------------------------------- |
| `Mail.Read`           | User             | Read email                      |
| `Mail.Send`           | User             | Send email                      |
| `Calendars.ReadWrite` | User             | Read and create calendar events |
| `Sites.Read.All`      | **Admin**        | Read SharePoint documents       |
| `Files.ReadWrite.All` | **Admin**        | Write SharePoint documents      |
| `ChannelMessage.Send` | **Admin**        | Post Teams messages             |

For the `m365_lite` script only `Mail.Read`, `Mail.Send`, and `Calendars.ReadWrite` are needed — no admin consent required.

After adding permissions, click **Grant admin consent for \<tenant\>** if you have admin rights, or ask your tenant admin to do so for the admin-only permissions.

### Configure Codemoo

Set the tenant and client IDs via environment variables:

```console
export CODEMOO_M365_TENANT_ID=<your-tenant-id>
export CODEMOO_M365_CLIENT_ID=<your-client-id>
export CODEMOO_M365_SHAREPOINT_HOST=<your-tenant>.sharepoint.com
export CODEMOO_M365_SHAREPOINT_SITE=/sites/<your-site>
```

### Authenticate

The first time you run in `m365` mode, Codemoo will print a device code and a URL:

```plain
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code ABCD1234 to authenticate.
```

Open the URL, enter the code, and sign in with your Microsoft account. The token is cached at `~/.cache/codemoo/token_cache.bin` so subsequent runs are silent for up to 90 days.

## Google Workspace

If you run in `workspace` mode, you need OAuth2 credentials from a Google Cloud project.

### Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **New Project**
2. Enable the APIs you need: **Gmail API**, **Google Calendar API**, **Google Chat API**, **Google Drive API**
3. Go to **APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID**
4. Choose **Desktop app**, download the JSON, and note the `client_id` and `client_secret`

### Configure Codemoo

Set the credentials via environment variables:

```console
export CODEMOO_WORKSPACE_CLIENT_ID=<your-client-id>
export CODEMOO_WORKSPACE_CLIENT_SECRET=<your-client-secret>
```

### Authenticate

The first time you run in `workspace` mode, Codemoo will print an authorization URL:

```plain
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
Enter the authorization code:
```

Open the URL, grant the requested permissions, and paste the authorization code back. The token is cached at `~/.cache/codemoo/workspace_token.pkl` so subsequent runs skip auth.

If you need to log out, or re-authenticate, then delete the token file.
