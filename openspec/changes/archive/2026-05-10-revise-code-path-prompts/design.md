## Context

The code-path demo runs eleven bots in sequence. Each bot's example prompts are
currently standalone demonstrations — readable individually but not forming a
story when watched end-to-end. The narrative arc described in the proposal
(reverse string thread → greeter Act 1 → tiemit Act 2) requires the prompt
files to be edited as a coherent set, with each bot's prompts designed to
follow from the previous bot's final state.

No infrastructure changes. The prompt files are plain `.txt` files with `---`
as a separator between prompts. The demo artifacts (greeter project in `demo/`)
are already in place.

## Goals / Non-Goals

**Goals:**
- Every code-path bot's prompts serve the continuous narrative
- Each prompt set is self-contained enough to work as a demo starting point
- Failure modes (ReadBot single-tool limit, missing file) are preserved as
  intentional teaching moments
- The tiemit arc is buildable across three bots without pre-seeded files

**Non-Goals:**
- Changing any bot system prompts, tool lists, or behavior
- M365 and Workspace paths (separate change)
- Automating demo reset — memory.md cleared manually before each demo run

## Decisions

### Shared bot prompts: "reverse string" thread starts at ChatBot

The reverse string thread begins at EchoBot but the key moment — asking for
the backwards spelling of "Guido van Rossum created Python" — first appears at
ChatBot. This is intentional: ChatBot can maintain the thread across turns, so
the spelling question lands as a natural escalation. SystemBot (Sona) gets the
same prompts but answers with a Python one-liner rather than attempting to
spell it, demonstrating persona effects. ToolBot closes the thread by actually
reversing it with a tool call.

**Alternative considered**: Starting the spelling prompt at LlmBot. Rejected
because LlmBot has no conversation memory — the question would arrive without
the "how do you reverse a string in Python / in C#" context that makes the
escalation feel natural.

### ReadBot failure modes are preserved, not fixed

Two prompts intentionally fail:
1. "Compare README.md and greeter.py" — ReadBot is a single-turn tool bot; it
   reads one file and cannot then read a second.
2. "What is the first line of archive.txt?" — the file does not exist.

These are kept because they demonstrate real limitations that ChangeBot then
overcomes. The contrast is the teaching moment.

### Act 1 prompts specify uv explicitly; Act 2 prompts from ProjectBot onward do not

Codemoo is designed to run within uv. Without explicit `uv run` in a prompt,
LLMs will default to plain `python` or `pytest` calls that may not resolve
correctly in the demo environment.

Act 1 prompts (ChangeBot, AgentBot) and the early Act 2 prompt (GuardBot's
test-and-commit step) MUST spell out the full command — `uv run greeter.py`,
`uv run pytest` — to avoid this failure mode.

ProjectBot is the turning point: it reads `demo/AGENTS.md`, which specifies
that `uv` is the required tool for all commands. From ProjectBot onward, prompts
can drop the `uv run` prefix. The bot infers it from project context. This is an
intentional teaching moment: AGENTS.md removes the need for callers to know
implementation details.

**Scope**: The GuardBot `uv init` prompt is already uv-specific by nature.
GuardBot's test-and-commit prompt still needs explicit `uv run pytest` because
GuardBot runs before ProjectBot loads AGENTS.md.

### ChangeBot's cat prompt contrasts explicitly with ReadBot's limitation

The prompt is worded to request a single command that shows both files, making
it obvious that the bot is circumventing the single-tool limitation via shell.
Suggested wording: "Show the contents of README.md and greeter.py with a
single shell command."

### tiemit built across three bots, not pre-seeded

tiemit/ does not exist in the repo. It is created live by GuardBot during the
demo. This means:
- GuardBot must scaffold the project with `uv init`
- GuardBot must write the initial CLI source
- ProjectBot reads what GuardBot wrote before making changes
- MemoryBot reads what ProjectBot wrote before adding the Streamlit frontend

Each bot in Act 2 depends on the actual filesystem state left by the previous
bot. Prompts must be written so the bot reads existing tiemit source before
modifying it.

**Risk**: If GuardBot's output is not committed or the demo is reset mid-session,
later bots will fail to find tiemit. Mitigation: demo resets start from the
greeter state; the Act 2 bots are understood to be sequential in a single
uninterrupted session.

### ProjectBot LLM upgrade uses Mistral API over openai package

The prompt specifies: openai package, base_url=`https://api.mistral.ai/v1`,
model=`mistral-small-latest`, API key from `MISTRAL_API_KEY` env var.

**Alternative considered**: Local ollama endpoint. Rejected in favor of Mistral
because it matches the codemoo config's preferred backend and Mistral's API is
more reliable for live demos than a local ollama instance.

**Note**: mistral-small is capable enough that it will sometimes succeed at
string reversal, which differs from the original simulated 70% failure rate.
This is acceptable — authentic LLM behavior is a better demo than simulation.

### MemoryBot color preference in same session

The planned mid-stream memory refresh shortcut does not yet exist. For now,
the color preference prompt and the Streamlit build prompt run in the same
conversation — MemoryBot picks up the preference from its conversation history.
When the refresh shortcut ships, the demo can be updated to demonstrate the
full cross-session memory flow without changing the prompts themselves.

## Risks / Trade-offs

- **tiemit CLI spec ambiguity** → The prompt must specify requirements clearly
  enough that the bot generates a working game, but without being so prescriptive
  that the code looks dictated. Leave room for the bot to make reasonable choices
  (variable names, structure) while specifying the required game mechanics.

- **Mistral API key required in demo environment** → Add to demo setup checklist;
  without `MISTRAL_API_KEY`, the ProjectBot LLM upgrade prompt will fail at
  runtime.

- **demo/.codemoo/memory.md must be empty at demo start** → No automation.
  Document in demo setup checklist. If memory is not cleared, MemoryBot will
  start with stale preferences and the "What do you know about me?" prompt
  produces a non-empty answer, breaking the arc.

## Open Questions

None — all decisions resolved during the exploration session that produced
this change.
