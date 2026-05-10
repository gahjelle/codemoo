## Context

The M365 and Workspace demo paths share the bot sequence `ScanBot → SendBot → AgentBot → GuardBot → ProjectBot → MemoryBot`. Currently these six bots run as isolated capability demos: each shows a tool working and stops. Several prompts are copy-pasted between platforms verbatim.

The code path has a well-structured arc: a concrete artifact (greeter.py) with real problems, a progressive build (tiemit/ grows across GuardBot → ProjectBot → MemoryBot), and a memory payoff (color preference → Streamlit UI). The platform paths need the same structure.

## Goals / Non-Goals

**Goals:**
- Give both platform paths a coherent narrative arc using a "back from vacation" scenario
- Introduce SingleTurnToolBot failure moments (teaching beats) in ScanBot and SendBot
- Create a progressive artifact build: GuardBot creates TEAM.md → ProjectBot reads it
- Make MemoryBot preferences produce visibly distinct output changes
- Keep M365 and Workspace prompts distinct in vocabulary and tone

**Non-Goals:**
- Changing bot system prompts (instructions) or tool configurations
- Changing the code path prompts
- Requiring actual emails/files to exist in the demo environment (prompts should work with a sparse inbox)

## Decisions

### Scenario: "Back from vacation"

Chosen over "project kickoff" and "follow up on a conversation." Rationale: universally relatable, escalates naturally from reading → responding → automating, and works when the inbox is sparse — the presenter describes the situation, the bot acts on what it finds.

### Shared scenario, platform-specific vocabulary

Both M365 and Workspace follow the same narrative beat-for-beat. M365 prompts reference SharePoint, Teams, Outlook. Workspace prompts reference Drive, Chat, Gmail. M365 tone is slightly more formal.

Alternative considered: different scenarios per platform. Rejected: harder to maintain and the scenario difference adds no demo value.

### TEAM.md as the progressive build artifact

GuardBot creates TEAM.md (the platform equivalent of `tiemit/` + `AGENTS.md`). Before writing, the agent asks the presenter for their manager's email — this interactive pause is a deliberate demo moment showing agent-driven information gathering.

TEAM.md content (prebaked except manager email):
```
Team: Oomedoc Maet
Project: Grassroots AI — investigating whether cows can be trained to
         replace AI assistants as a sustainable alternative to LLMs
Members: Clara, Owen, Wendy
Standup: Mondays 10:30am
Channel: #moo
Communication: formal for external stakeholders, casual internally
Manager: <collected interactively>
```

"Oomedoc Maet" is Team Codemoo spelled backwards. Member initials spell COW.

### Fixed TEAM.md path

GuardBot writes to a known path (SharePoint site root for M365, Drive root for Workspace). ProjectBot reads from the same path. This must be explicit in both prompts — if the path is ambiguous, ProjectBot silently fails to find context.

### Three MemoryBot preferences with distinct visible payoffs

| Preference | Visible change |
|---|---|
| Always cc manager on external emails | CC field populated from TEAM.md manager address |
| Include a mathematical fun-fact after my name | Fun-fact line appears in email body |
| No meetings before 10am | Calendar events land at 10am or later |

Each preference changes a different part of the output (fields, body, time). The fun-fact is intentionally surprising — it makes the memory payoff memorable.

### SingleTurnToolBot failure prompts

ScanBot and SendBot are `SingleTurnToolBot` instances — one tool call per turn. The second prompt in each bot intentionally requests two actions, hitting this limit. This mirrors the ReadBot teaching pattern in the code path.

- ScanBot failure: "What day is it, and how does my calendar look this week?" (get_datetime + list_cal = two calls)
- SendBot failure: "Draft a reply to the status email AND create a calendar block for the report." (two write calls)

The ScanBot failure prompt also bridges from ToolBot: `get_datetime` is a tool ToolBot just demonstrated, so asking for the date here connects the chapters.

## Risks / Trade-offs

**TEAM.md path drift** → Both GuardBot and ProjectBot prompts must name an identical path. If they diverge, the demo silently fails at ProjectBot. Mitigation: design doc and task description both call this out explicitly.

**Sparse inbox** → AgentBot's "find everything needing a reply" prompt produces thin output with an empty inbox. Mitigation: demo setup doc recommends seeding 2-3 emails before the demo, but prompts are written to degrade gracefully.

**#moo channel must exist** → SendBot posts to `#moo` on first write. If the channel doesn't exist, the tool call fails. Mitigation: demo setup doc lists this as a required pre-demo step.

**Manager email interactivity** → GuardBot must ask a question and wait for the answer before writing TEAM.md. GuardBot is a full conversational bot (not SingleTurnToolBot), so multi-turn within a session works. This is the expected behavior.
