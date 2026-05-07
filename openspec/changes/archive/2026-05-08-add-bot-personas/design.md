## Context

The Codemoo demo uses a progression of bots, each introducing a new capability. Sona (SystemBot) demonstrates how a strong system prompt shapes personality — her prompt is deliberately extreme for demo effect. The bots after Sona (Telo through Lore) have minimal, inconsistent prompts written ad-hoc. They lack consistent structure, contain scattered terminology inconsistencies ("helpful coding assistant" vs "coding assistant", Lore calling itself a "business assistant"), and have no personality beyond being functional.

The named tool lists in `codemoo.toml` also carry `reverse_string` in every entry. `reverse_string` was introduced as a teaching tool for Telo but its presence in Axel's and Loom's toolkits alongside `run_shell` and `write_file` is incongruous and muddies the demo narrative.

## Goals / Non-Goals

**Goals:**
- Consistent four-part structure across all 17 post-Sona instruction files
- Each bot gains a credo — a short operating-principle phrase baked into its system prompt
- `reverse_string` scoped to Telo only; removed from all named tool lists
- Pattern documented in AGENTS.md for future bot authors

**Non-Goals:**
- Sona's prompt is not changed — her extreme persona is intentional
- No new bot types or variants
- No changes to bot behavior, tool implementations, or the TUI
- No changes to how system prompts are loaded or applied

## Decisions

### Four-part form over cumulative stacking

Each bot's system prompt describes its own capability without inheriting descriptions from previous bots. Cumulative stacking (each prompt listing all tools available to it) was considered but rejected: (a) the tool config in `codemoo.toml` already declares the capability set, (b) stacking produces increasingly long, repetitive prompts, (c) each prompt should emphasize what's *new*, not inventory everything. The tool list is the capability declaration; the system prompt is the behavior declaration.

### Credo as last line, not adjective prefix

Personality could be expressed as an adjective in the identity line ("You are Telo, a methodical coding assistant") or as a final credo phrase. The credo-as-last-line approach is preferred because: (a) it reads as instruction to the LLM, shaping behavior rather than just labeling a trait, (b) a short memorable phrase can occasionally surface naturally in responses as an easter egg, (c) a single adjective is thin; the credo has room for nuance.

### Same credo across variants, vocabulary adapts

Each bot has one credo that appears identically across all its variants. Domain vocabulary (e.g. "email, calendar, SharePoint" vs "Gmail, Calendar, Drive") adapts within the body of the prompt, but the credo line is invariant. This keeps each bot's identity coherent while allowing the body to be domain-specific.

**Credo reference:**

| Bot | Credo |
|-----|-------|
| Telo (ToolBot) | A tool call now beats an assumption later. |
| Rune (ReadBot) | The code tells its own story. |
| Roam (ScanBot) | Observe everything, report accurately, change nothing. |
| Axel (ChangeBot) | Changes leave marks — make them count. |
| Aero (SendBot) | Once sent, it can't be recalled. |
| Loom (AgentBot) | Follow the thread — one call at a time — until the task is done. |
| Cato (GuardBot) | Caution isn't hesitation — it's precision. |
| Lore (ProjectBot) | Context first — conventions are rarely arbitrary. |

### reverse_string scoped to Telo via direct assignment

`reverse_string` is already assigned directly to Telo's variant (not via a named list). Removing it from all named lists silently scopes it to Telo with no change to Telo itself. This is the path of least disruption: no new named lists, no Telo-specific override needed.

### Role taxonomy: two roles, no adjective prefix

Two roles only — `coding assistant` for code variants, `productivity assistant` for M365 and Workspace variants. No adjective prefix ("helpful", "business"). Sona uses "ruthlessly practical coding assistant" as the intentional exception that demonstrates what a strong persona looks like.

### Platform variants run to four sentences

Code variants are ~3 sentences. Platform (M365/Workspace) variants are ~4 because explicitly listing available API tools adds context the user may not know — unlike file and shell tools, M365 and Workspace API capabilities are not self-evident.

## Risks / Trade-offs

- **LLM ignores the credo** → Mitigation: the credo is phrased as an instruction ("follow the thread"), not a personality label, which makes it more likely to shape behavior.
- **reverse_string removal breaks demo prompts that reference it by name** → Mitigation: example prompt files should be checked; the tool remains in Telo's toolkit, so any Telo prompts that use it still work.
- **Rewriting 17 files introduces regressions** → Mitigation: each new prompt is strictly focused — no behavioral instructions are removed, only restructured and a credo appended.
