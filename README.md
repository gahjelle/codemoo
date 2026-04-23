# Codemoo - Demonstrate how coding agents work under the hood

Requirements:

- `uv`
- Mistral API key set as `MISTRAL_API_KEY`

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

Run through the bot progression to see how coding agents evolve step by step — from a simple echo bot up to a full agent loop:

```console
uv run codemoo demo
```

Each bot is introduced with slides explaining what it can do and how it works. Press **Ctrl-N** to advance to the next bot, or **Ctrl-Q** to quit.

Start the demo from a specific bot:

```console
uv run codemoo demo --start ash
```

### Bot progression

| #   | Bot    | Capability                                    |
| --- | ------ | --------------------------------------------- |
| 1   | 🦜 Coco | Echo — repeats your message back              |
| 2   | ✨ Mono | LLM — single-turn language model call         |
| 3   | 🧿 Iris | Chat — multi-turn conversation with history   |
| 4   | 🎭 Sona | System prompt — chat with a persona           |
| 5   | 🔧 Telo | Tools — can call a tool and act on the result |
| 6   | 📁 Rune | Files — can read and write files              |
| 7   | 🐚 Ash  | Shell — can run shell commands                |
| 8   | 🌀 Loom | Agent — full agentic loop with planning       |
