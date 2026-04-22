## Context

Codemoo is a demo chain of bots, each adding one capability. ToolBot (#5) already demonstrates the full tool-call round-trip using a trivial `reverse_string` tool. FileBot (#6) is the next step: it gives the LLM access to the filesystem by swapping in a `read_file` tool and file-oriented instructions.

The project is structured so that every bot is an independent dataclass following the `ChatParticipant` protocol — no bot subclasses another. Tools live in `codemoo.core.tools` and are passed to any bot that needs them at construction.

## Goals / Non-Goals

**Goals:**
- Add a `read_file` tool definition to the tools module
- Add `FileBot`, a new bot dataclass wired with `read_file` and instructions that encourage file inspection
- Register FileBot in the CLI (and TUI bot selection when it exists)

**Non-Goals:**
- Path sandboxing or access control — this is a demo, not a production tool
- Writing, editing, or listing files — one tool, one capability
- Subclassing or reusing ToolBot's class — FileBot is its own dataclass, consistent with project pattern

## Decisions

### FileBot is a standalone dataclass, not a subclass of ToolBot

Every bot in the chain (EchoBot, LLMBot, ChatBot, SystemBot, ToolBot) is a self-contained dataclass. Subclassing would add coupling for no gain — the constructor fields and `on_message` implementation are identical in shape to ToolBot.

_Alternative considered_: Inherit from ToolBot or introduce a shared `ToolBasedBot` base. Rejected because it adds abstraction the demo doesn't need and the bots are already simple enough to read in full.

### read_file returns a string (including error messages), never raises

When a path doesn't exist or can't be read, `read_file.fn` returns a descriptive error string instead of raising. This lets the LLM report the problem gracefully without requiring any exception handling in FileBot's `on_message`.

_Alternative considered_: Raise `FileNotFoundError` and let FileBot catch it. Rejected because it would add control-flow complexity to a bot that's supposed to be identical in shape to ToolBot.

### FileBot uses the same on_message logic as ToolBot

FileBot's `on_message` is structurally identical to ToolBot's: call `complete_step`, check for `ToolUse`, invoke the tool, re-complete. The only meaningful differences are the tool list and system instructions.

## Risks / Trade-offs

- **Unrestricted path access** → Acceptable for a demo context; the README/script should note this is intentional.
- **Large files can exhaust the LLM context window** → Acceptable; the demo uses small files. Future bots (ShellBot, AgentBot) will address more capable file handling.

## Migration Plan

No migration needed — FileBot is a purely additive change. No existing bot or API is modified.
