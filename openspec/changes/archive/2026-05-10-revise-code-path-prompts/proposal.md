## Why

The demo's bot sequence has potential as a teaching narrative, but the current
example prompts are largely disconnected — each bot demonstrates its own
capability without building on what came before. Reshaping them into a
continuous two-act story makes each bot's capability feel meaningful in context
rather than illustrative in isolation.

## What Changes

- Revise all 11 code-path example prompt files to form a continuous narrative arc
- Clear `demo/.codemoo/memory.md` so each demo run starts with a blank memory slate

### The arc

**Shared bots — "reverse string" thread**: Each bot gets the same concept
(reversing a string), revealing a new limitation or capability in sequence:
EchoBot mirrors, LlmBot answers, ChatBot maintains context, SystemBot (Sona)
responds with code rather than spelling it out, ToolBot actually does it with
a tool call.

**Act 1 — The Greeter (understand → fix → autonomous fix)**: ReadBot reads
greeter.py and encounters intentional failure modes (single-tool limitation,
missing file). ChangeBot overcomes those limitations with shell commands.
AgentBot fixes the bug autonomously in a single prompt.

**Act 2 — Building tiemit**: GuardBot scaffolds `tiemit/` (a Human vs AI
String Reversal Challenge — "timeit" spelled backwards) as a CLI with a fake
random AI, pausing before each write. ProjectBot reads demo/AGENTS.md, creates
an AGENTS.md for tiemit, then upgrades the fake AI to a real Mistral LLM call.
MemoryBot learns a UI color preference, then builds the Streamlit frontend
using that preference.

## Capabilities

### New Capabilities

None — this change only modifies prompt content and demo artifact state.

### Modified Capabilities

- `demo-artifacts`: `demo/AGENTS.md` must be present as a required demo artifact
  (it already exists, but is not covered by the current spec). `demo/.codemoo/memory.md`
  must be defined as empty-at-demo-start.

## Non-Goals

- M365 and Workspace prompt paths (separate change)
- Any changes to bot behavior, tools, or system prompts
- Changes to demo infrastructure, TUI, or configuration loading

## Impact

- 11 example prompt `.txt` files under `src/codemoo/config/example_prompts/`
- `demo/.codemoo/memory.md` (cleared to empty)
- `demo-artifacts` spec updated to cover AGENTS.md and memory.md reset requirement
