# Codemoo - Demonstrate how coding agents work under the hood

Requirements:

- `uv`
- An API key for either Mistral, Openrouter, or Anthropic

## Configuration

| Variable                   | Default                     | Description                                              |
| -------------------------- | --------------------------- | -------------------------------------------------------- |
| `CODEMOO_LANGUAGE`         | `English`                   | Language for commentary, error messages, and demo slides |
| `CODEMOO_BACKEND`          | `mistral`                   | Name of LLM backend: mistral, openrouter, or anthropic   |
| `MISTRAL_API_KEY`          | —                           | Mistral API key (required for mistral backend)           |
| `CODEMOO_MISTRAL_MODEL`    | `mistral-small-latest`      | Mistral model used for all LLM calls                     |
| `OPENROUTER_API_KEY`       | —                           | Openrouter API key (required for openrouter backend)     |
| `CODEMOO_OPENROUTER_MODEL` | `z-ai/glm-4.5-air:free`     | Openrouter model used for all LLM calls                  |
| `ANTHROPIC_API_KEY`        | —                           | Anthropic API key (required for anthropic backend)       |
| `CODEMOO_ANTHROPIC_MODEL`  | `claude-haiku-4-5-20251001` | Anthropic model used for all LLM calls                   |

## Installation

```console
uv sync
```

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

### Bot progression

| #   | Bot    | Capability                                     |
| --- | ------ | ---------------------------------------------- |
| 1   | 🦜 Coco | Echo — repeats your message back               |
| 2   | ✨ Mono | LLM — single-turn language model call          |
| 3   | 🧿 Iris | Chat — multi-turn conversation with history    |
| 4   | 🎭 Sona | System prompt — chat with a persona            |
| 5   | 🔧 Telo | Tools — can call a tool and act on the result  |
| 6   | 📁 Rune | Files — can read and write files               |
| 7   | 🐚 Ash  | Shell — can run shell commands                 |
| 8   | 🌀 Loom | Agent — full agentic loop with planning        |
| 9   | 🔒 Cato | Guard — human-in-the-loop before risky actions |

See [BOTS.md](BOTS.md) for more information about the bots.