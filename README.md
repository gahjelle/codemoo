# Codemoo - Demonstrate how coding agents work under the hood

Requirements:

- `uv`
- An API key for at least one LLM provider (Mistral, OpenAI, Google, OpenRouter, or Anthropic), or a running [Ollama](https://ollama.com) server for local use
- Microsoft Graph access is required for `m365` mode — see [Microsoft Graph setup](docs/setup/microsoft-graph.md)
- Google Workspace OAuth credentials are required for `workspace` mode — see [Google Workspace setup](docs/setup/google-workspace.md)

## Installation

You should install Codemoo as a tool:

```console
uv tool install . --editable
```

> **Important:** Some of the demo bots can run destructable commands without any confirmation. Be careful with your prompts!

## Configuration

Codemoo can run in several modes:

- **`code`** is the default mode where it is your friendly coding assistant (similar to Claude Code, OpenCode, Codex, and GitHub Copilot).
- **`m365`** requires access to [Microsoft Graph](docs/setup/microsoft-graph.md) and gives Codemoo access to your Outlook email, Teams, Calendar, and SharePoint — similar to M365 Copilot.
- **`workspace`** requires [Google Workspace](docs/setup/google-workspace.md) OAuth credentials and gives Codemoo access to Gmail, Google Calendar, and Google Chat.

**General Setup**

| Variable           | Default   | Description                                                          |
| ------------------ | --------- | -------------------------------------------------------------------- |
| `CODEMOO_LANGUAGE` | `English` | Language for commentary, error messages, and demo slides and prompts |

**LLM Backends**

Codemoo will try all different LLM backends until it finds one that is set up. The priority order is: `mistral` → `openrouter` → `google` → `anthropic` → `openai` → `ollama`.

| Variable          | Default | Description                                                                                                                    |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `CODEMOO_BACKEND` | —       | Force a specific backend (`mistral`, `ollama`, `openrouter`, `google`, `anthropic`, `openai`). Raises an error if unavailable. |

To set up an LLM backend, provide an API key. You can optionally override the model. Codemoo shows the active backend and model in the lower right corner.

| Variable                   | Default                     | Description                                                                       |
| -------------------------- | --------------------------- | --------------------------------------------------------------------------------- |
| `MISTRAL_API_KEY`          | —                           | Mistral API key (required for mistral backend)                                    |
| `CODEMOO_MISTRAL_MODEL`    | `mistral-small-latest`      | Mistral model override                                                            |
| `OPENROUTER_API_KEY`       | —                           | OpenRouter API key (required for openrouter backend)                              |
| `CODEMOO_OPENROUTER_MODEL` | `z-ai/glm-4.5-air:free`     | OpenRouter model override                                                         |
| `GOOGLE_API_KEY`           | —                           | Google AI API key (required for google backend)                                   |
| `CODEMOO_GOOGLE_MODEL`     | `gemini-2.0-flash`          | Google model override                                                             |
| `ANTHROPIC_API_KEY`        | —                           | Anthropic API key (required for anthropic backend)                                |
| `CODEMOO_ANTHROPIC_MODEL`  | `claude-haiku-4-5-20251001` | Anthropic model override                                                          |
| `OPENAI_API_KEY`           | —                           | OpenAI API key (required for openai backend)                                      |
| `CODEMOO_OPENAI_MODEL`     | `gpt-4o-mini`               | OpenAI model override                                                             |
| `OLLAMA_API_KEY`           | `ollama`                    | Ollama API key (optional; defaults to `ollama` for unauthenticated local servers) |
| `CODEMOO_OLLAMA_MODEL`     | `qwen2.5-coder:7b`          | Ollama model override                                                             |

For local Ollama usage, install [Ollama](https://ollama.com), pull a model (`ollama pull qwen2.5-coder:7b`), and set `CODEMOO_BACKEND=ollama`. No API key is required. The `base_url` for each provider can also be overridden in a local `codemoo.toml` — useful for pointing the `openai` backend at Azure AI Foundry or other compatible endpoints.

## Usage

Codemoo has two main modes: a coding assistant you can use directly, and a step-by-step demo that shows how coding agents work under the hood.

### Coding assistant

Launch the chat with the most capable bot:

```console
uv run codemoo
```

The business chat is named Collebra, and can be run in the same way as Codemoo (requires a Google workspace registration and correctly set [environment variables](#configuration)):

```console
uv run collebra
uv run codemoo --variant workspace
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

For the **M365 and Workspace demo paths**, some setup is required before running (creating a `moo` channel, seeding emails, etc.). See [`docs/setup/demo-setup.md`](docs/setup/demo-setup.md) for the full checklist.

Start the interactive demo:

```console
uv run codemoo demo
```

Each bot is introduced with slides explaining what it can do and how it works. Press **Ctrl-N** to advance to the next bot, or **Ctrl-Q** to quit. Press **Ctrl-S** at any point to reopen the current bot's slide. Each bot also comes with a few example prompts — press **Ctrl-E** to insert the next one, then edit or press **Enter** to submit. You can inspect the current context with **Ctrl-X** and see a trace of the requests and responses for the last turn with **Ctrl-T**. The input field supports multiple lines with **Alt+N**.

You can start or end the demo at specific bots:

```console
uv run codemoo demo --start telo --end loom
```

Or run with different preset scripts:

```console
uv run codemoo list-scripts
uv run codemoo demo --script focused
```

Scripts can also be further customized with `--start` and `--end`.

## Bot Progression

**Coding path** (`--script all`):

| #   | Bot    | Capability                                       |
| --- | ------ | ------------------------------------------------ |
| 1   | 🦜 Coco | Echo — repeats your message back                 |
| 2   | ✨ Mono | LLM — single-turn language model call            |
| 3   | 🧿 Iris | Chat — multi-turn conversation with history      |
| 4   | 🎭 Sona | System prompt — chat with a persona              |
| 5   | 🔧 Telo | Tools — can call a tool and act on the result    |
| 6   | 📁 Rune | ReadBot — reads files and lists directories      |
| 7   | 🔨 Axel | ChangeBot — runs shell commands and writes files |
| 8   | 🌀 Loom | Agent — full agentic loop with planning          |
| 9   | 🐦 Crow | RetryBot — tool errors feed back to the LLM      |
| 10  | 🔒 Lock | Guard — human-in-the-loop before risky actions   |
| 11  | 🎤 Aria | ProjectBot — inject information in every call    |
| 12  | 🐻 Ursa | MemoryBot — persists context across sessions     |
| 13  | 🧹 Drop | CompactBot — summarises context when it grows    |

The M365 (`--script m365`) and Workspace (`--script workspace`) paths follow the same progression but replace ReadBot and ChangeBot with platform-specific bots (ScanBot and SendBot) that read and write Outlook/Teams and Gmail/Calendar respectively. See [BOTS.md](BOTS.md) for the full breakdown.
