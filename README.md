# Codemoo - Demonstrate how coding agents work under the hood

Requirements:

- `uv`
- An API key for either Mistral, Openrouter, or Anthropic
- Microsoft Graph access is required for `m365` mode

## Installation

You should install Codemoo as a tool:

```console
uv tool install . --editable
```

> **Important:** Some of the demo bots can run destructable commands without any confirmation. Be careful with your prompts!

## Configuration

Codemoo can run in two different modes:

- **`code`** is the default mode where it is your friendly coding assistant (similar to Claude Code, OpenCode, Codex, and GitHub Copilot).
- **`m365`** requires access to [Microsoft Graph](#microsoft-graph) and gives Codemoo access to your E-mail, Teams, Calendar and Sharepoint, very much like M365 Copilot.

**General Setup**

| Variable           | Default   | Description                                                          |
| ------------------ | --------- | -------------------------------------------------------------------- |
| `CODEMOO_LANGUAGE` | `English` | Language for commentary, error messages, and demo slides and prompts |

**LLM Backends**

| Variable                   | Default                     | Description                                            |
| -------------------------- | --------------------------- | ------------------------------------------------------ |
| `CODEMOO_BACKEND`          | `mistral`                   | Name of LLM backend: mistral, openrouter, or anthropic |
| `MISTRAL_API_KEY`          | —                           | Mistral API key (required for mistral backend)         |
| `CODEMOO_MISTRAL_MODEL`    | `mistral-small-latest`      | Mistral model used for all LLM calls                   |
| `OPENROUTER_API_KEY`       | —                           | Openrouter API key (required for openrouter backend)   |
| `CODEMOO_OPENROUTER_MODEL` | `z-ai/glm-4.5-air:free`     | Openrouter model used for all LLM calls                |
| `ANTHROPIC_API_KEY`        | —                           | Anthropic API key (required for anthropic backend)     |
| `CODEMOO_ANTHROPIC_MODEL`  | `claude-haiku-4-5-20251001` | Anthropic model used for all LLM calls                 |

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

Use `--bot` to start with a specific bot by name, type, or 1-based index:

```console
uv run codemoo --bot rune
uv run codemoo --bot 6
```

Use `--mode` to switch to the M365 Copilot path (requires an Entra app registration and correctly set [environment variables](#configuration).):

```console
uv run codemoo --mode m365
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

Each bot is introduced with slides explaining what it can do and how it works. Press **Ctrl-N** to advance to the next bot, or **Ctrl-Q** to quit. Each bot also comes with a few example prompts. Press **Ctrl-E** to insert the next example prompt. You can then edit it or just press enter to submit it directly.

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

| #   | Bot        | Capability                                       |
| --- | ---------- | ------------------------------------------------ |
| 1   | 🦜 Coco     | Echo — repeats your message back                 |
| 2   | ✨ Mono     | LLM — single-turn language model call            |
| 3   | 🧿 Iris     | Chat — multi-turn conversation with history      |
| 4   | 🎭 Sona     | System prompt — chat with a persona              |
| 5   | 🔧 Telo     | Tools — can call a tool and act on the result    |
| 6   | 📁 **Rune** | ReadBot — reads files and lists directories      |
| 7   | 🔨 **Axel** | ChangeBot — runs shell commands and writes files |
| 8   | 🌀 Loom     | Agent — full agentic loop with planning          |
| 9   | 🔒 Cato     | Guard — human-in-the-loop before risky actions   |

**M365 path** (`--script m365`):

| #   | Bot        | Capability                                            |
| --- | ---------- | ----------------------------------------------------- |
| 1   | 🦜 Coco     | Echo — repeats your message back                      |
| 2   | ✨ Mono     | LLM — single-turn language model call                 |
| 3   | 🧿 Iris     | Chat — multi-turn conversation with history           |
| 4   | 🎭 Sona     | System prompt — chat with a persona                   |
| 5   | 🔧 Telo     | Tools — can call a tool and act on the result         |
| 6   | 🚶 **Roam** | ScanBot — reads SharePoint, email, and calendar       |
| 7   | 📤 **Aero** | SendBot — sends email, creates events, posts to Teams |
| 8   | 🌀 Loom     | Agent — full agentic loop over M365 data              |
| 9   | 🔒 Cato     | Guard — human approval before M365 actions            |

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