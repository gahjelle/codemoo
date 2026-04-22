## Context

`ToolBot` and `FileBot` are structurally identical — same `on_message` logic, same fields, same LLM round-trip. The only differences are the default `instructions` string and the docstring. `ShellBot` would be a third copy. The user's instruction is to extract a `GeneralToolBot` base class that holds the shared implementation, while keeping the three concrete bot classes as separate, named modules for pedagogical clarity.

The `run_shell` tool needs to execute real shell commands and capture their output. This is explicitly the "dangerous" step in the demo arc — the point is to show what happens when an LLM can touch the world.

## Goals / Non-Goals

**Goals:**
- Introduce `GeneralToolBot` as a concrete dataclass that owns the single-round-trip tool-call logic.
- Refactor `ToolBot` and `FileBot` to inherit from `GeneralToolBot` with no behavioural change.
- Add `ShellBot` (name "Ash", emoji 🐚) as a third subclass with shell-execution instructions.
- Add `run_shell` tool using `subprocess`.
- Register Ash in `codemoo/__init__.py`.

**Non-Goals:**
- Multi-tool-call / agentic loops (that is AgentBot's job).
- Command sandboxing or allowlisting — the unsafety is the demo point.
- Async subprocess execution.
- Streaming shell output.

## Decisions

### `GeneralToolBot` as dataclass base class, subclasses re-declare `instructions` with a default

**Chosen:** `GeneralToolBot` declares `instructions: str` with no default. Each subclass re-declares `instructions: str = _INSTRUCTIONS` with its own module-level constant. Python dataclass inheritance allows this; the child's re-declaration replaces the parent's field, and the positional ordering (`name, emoji, backend, human_name, tools` — all required — before `instructions, max_messages` — both with defaults) remains valid.

**Alternatives considered:**
- *Standalone helper function* — `_respond_with_tool(self, message, history)` shared via import. Avoids inheritance but requires each bot to call it explicitly, which is more boilerplate and less obviously "the same bot".
- *ABC with abstract `instructions`* — overly complex; Python ABCs and dataclasses interact awkwardly, and `instructions` is data, not a method.
- *Copy-paste the three classes* — simplest file-by-file, but three copies of identical logic will inevitably drift.

### `run_shell` uses `subprocess.run` with `shell=True`

**Chosen:** `subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)`. Returns a formatted string with stdout, stderr, and exit code. Shell-mode allows pipelines and built-ins (which the LLM is likely to use).

**Alternatives considered:**
- *`shell=False` with shlex split* — safer, but the LLM generates shell strings; splitting them reliably is complex and would break pipelines.
- *Async subprocess* — not needed yet; blocking is fine for a demo bot with a timeout.

### Error output included in return value, not raised as exception

**Chosen:** Non-zero exit codes and stderr are returned as part of the tool's string output (not raised). This lets the LLM see the error and potentially recover or explain it to the user.

**Rationale:** From the LLM's perspective, a failing command is information, not an exception.

### Name: Ash

Ash is an actual Unix shell (the Almquist shell, used in BusyBox). It's short (3 letters), starts with A as required, and the shell pun is immediate. Alternative names considered:
- **Arco** — suggests trajectory/arc, not shell-specific
- **Argo** — nice, but evokes Kubernetes more than shell execution
- **Axel** — no shell connection

Ash wins on directness and the existing SCRIPT.md entry.

## Risks / Trade-offs

- **Arbitrary shell execution** — `run_shell` will run anything the LLM asks. This is intentional for the demo (the talking point is "now it can run code — this is where it gets dangerous"), but demos must be run in safe environments. No mitigation in code; document in demo notes.
- **Timeout** — default 30 s. Long-running commands (builds, downloads) will be cut off. The LLM will see a timeout error in the output; it can't retry with different args automatically (no agentic loop yet).
- **Dataclass inheritance subtlety** — re-declaring a field in a child dataclass is valid Python but not widely known. A reader unfamiliar with the pattern may be confused. Mitigated by a comment in `GeneralToolBot` and the fact that each bot file is self-contained.

## Migration Plan

1. Create `general_tool_bot.py` with the shared implementation.
2. Update `tool_bot.py` and `file_bot.py` to inherit — no public API change, all existing tests pass unchanged.
3. Add `run_shell` tool, `shell_bot.py`, and register Ash.
4. No database migrations, no API changes, no deploy steps.
