## 1. Tool list cleanup

- [x] 1.1 Remove `reverse_string` from `code_read` in `codemoo.toml`
- [x] 1.2 Remove `reverse_string` from `code_write` in `codemoo.toml`
- [x] 1.3 Remove `reverse_string` from `m365_read` in `codemoo.toml`
- [x] 1.4 Remove `reverse_string` from `m365_write` in `codemoo.toml`
- [x] 1.5 Remove `reverse_string` from `workspace_read` in `codemoo.toml`
- [x] 1.6 Remove `reverse_string` from `workspace_write` in `codemoo.toml`

## 2. Code path instruction files

- [x] 2.1 Rewrite `tool_bot-default.txt` — identity + capability + trigger + credo "A tool call now beats an assumption later."
- [x] 2.2 Rewrite `read_bot-code.txt` — identity + read capability + trigger (read don't assume) + credo "The code tells its own story."
- [x] 2.3 Rewrite `change_bot-code.txt` — identity + execute/write capability + trigger + credo "Changes leave marks — make them count."
- [x] 2.4 Rewrite `agent_bot-code.txt` — identity + loop capability + trigger + credo "Follow the thread — one call at a time — until the task is done."
- [x] 2.5 Rewrite `guard_bot-code.txt` — identity + approval capability + trigger (adapt if denied) + credo "Caution isn't hesitation — it's precision."
- [x] 2.6 Rewrite `project_bot-code.txt` — identity + context-first capability + trigger + credo "Context first — conventions are rarely arbitrary."

## 3. M365 path instruction files

- [x] 3.1 Rewrite `scan_bot-m365.txt` — productivity assistant + M365 read tools listed + read-only trigger + credo "Observe everything, report accurately, change nothing."
- [x] 3.2 Rewrite `send_bot-m365.txt` — productivity assistant + M365 write tools listed + action trigger + credo "Once sent, it can't be recalled."
- [x] 3.3 Rewrite `agent_bot-m365.txt` — productivity assistant + M365 tools listed + loop trigger + credo "Follow the thread — one call at a time — until the task is done."
- [x] 3.4 Rewrite `guard_bot-m365.txt` — productivity assistant + M365 tools listed + approval trigger with real-consequences note + credo "Caution isn't hesitation — it's precision."
- [x] 3.5 Rewrite `project_bot-m365.txt` — productivity assistant + M365 tools listed + SharePoint context trigger + credo "Context first — conventions are rarely arbitrary."

## 4. Workspace path instruction files

- [x] 4.1 Rewrite `scan_bot-workspace.txt` — productivity assistant + Workspace read tools listed + read-only trigger + credo "Observe everything, report accurately, change nothing."
- [x] 4.2 Rewrite `send_bot-workspace.txt` — productivity assistant + Workspace write tools listed + action trigger + credo "Once sent, it can't be recalled."
- [x] 4.3 Rewrite `agent_bot-workspace.txt` — productivity assistant + Workspace tools listed + loop trigger + credo "Follow the thread — one call at a time — until the task is done."
- [x] 4.4 Rewrite `guard_bot-workspace.txt` — productivity assistant + Workspace tools listed + approval trigger with real-consequences note + credo "Caution isn't hesitation — it's precision."
- [x] 4.5 Rewrite `project_bot-workspace.txt` — productivity assistant + Workspace tools listed + Drive context trigger + credo "Context first — conventions are rarely arbitrary."

## 5. Documentation

- [x] 5.1 Add "Bot System Prompt Style" subsection to `AGENTS.md` under Bot Configuration: four-part form, role naming rules, credo concept, credo reference table, `reverse_string` convention
- [x] 5.2 Update the stale `code_write` example in the `[tool_lists]` description in `AGENTS.md` to remove `reverse_string`
- [x] 5.3 Add Bot Character Reference table to `BOTS.md` with all bot credos; mark unimplemented bot credos as provisional with a note to revisit at implementation time

  Implemented (final):
  Telo — "A tool call now beats an assumption later."
  Rune — "The code tells its own story."
  Roam — "Observe everything, report accurately, change nothing."
  Axel — "Changes leave marks — make them count."
  Aero — "Once sent, it can't be recalled."
  Loom — "Follow the thread — one call at a time — until the task is done."
  Cato — "Caution isn't hesitation — it's precision."
  Lore — "Context first — conventions are rarely arbitrary."

  Provisional (revisit when implemented):
  Aura — "Past turns are future context."
  Undo — "A stumble is just data."
  Draw — "Sketch before you cut."
  Exec — "One name, one action, every time."
  Coda — "The playbook comes before the task."
  Omni — "One turn, many moves."
  Dual — "The first answer is always a draft."
  Enum — "Divide the goal, multiply the effort."
  Cast — "Structure is the contract between thinking and action."
  Scout — "The answer is out there — go find it."
  Mesh — "Every tool deserves a seat at the table."
  Pith — "Keep only what still matters."
  Codemoo — "Everything, working together."

## 6. Verification

- [x] 6.1 Run `uv run ruff format src/ tests/` and fix any issues
- [x] 6.2 Run `uv run ruff check src/ tests/` and fix any issues
- [x] 6.3 Run `uv run ty check src/ tests/` and fix any issues
- [x] 6.4 Run `uv run pytest` and confirm all tests pass
- [x] 6.5 Smoke-test the default script: step through Telo → Rune → Axel and verify prompts appear correct in the TUI
