## 1. ScanBot Prompts (both platforms)

- [x] 1.1 Revise `scan_bot-m365.txt`: "back from vacation" opener, SingleTurnToolBot failure prompt (day + calendar), third single-action prompt (SharePoint check)
- [x] 1.2 Revise `scan_bot-workspace.txt`: same arc, Workspace vocabulary (Gmail, Calendar, Drive)

## 2. SendBot Prompts (both platforms)

- [x] 2.1 Revise `send_bot-m365.txt`: post to #moo Teams channel, SingleTurnToolBot failure prompt (reply + calendar block), recover with single draft action
- [x] 2.2 Revise `send_bot-workspace.txt`: same arc, Workspace vocabulary (Chat, Gmail, Calendar)

## 3. AgentBot Prompts (both platforms)

- [x] 3.1 Revise `agent_bot-m365.txt`: tool orientation prompt, then full autonomous backlog triage (scan inbox, draft replies, create reminders)
- [x] 3.2 Revise `agent_bot-workspace.txt`: same arc, Workspace vocabulary

## 4. GuardBot Prompts (both platforms)

- [x] 4.1 Revise `guard_bot-m365.txt`: summarise draft reply, send with approval pause, then create TEAM.md (ask for manager email before writing to SharePoint root)
- [x] 4.2 Revise `guard_bot-workspace.txt`: same arc, write TEAM.md to Drive root

## 5. ProjectBot Prompts (both platforms)

- [x] 5.1 Revise `project_bot-m365.txt`: read TEAM.md from SharePoint root, draft stakeholder update email using team context, schedule team sync respecting 10am preference
- [x] 5.2 Revise `project_bot-workspace.txt`: same arc, read TEAM.md from Drive root

## 6. MemoryBot Prompts (both platforms)

- [x] 6.1 Revise `memory_bot-m365.txt`: recall preferences, set all three (manager CC, math fun-fact, no meetings before 10am), send stakeholder update applying all preferences
- [x] 6.2 Revise `memory_bot-workspace.txt`: same three preferences, Workspace vocabulary

## 7. Demo Artifacts

- [x] 7.1 Create `demo/TEAM.md` with prebaked content: team Oomedoc Maet, Grassroots AI project, members Clara/Owen/Wendy, standup Mondays 10:30am, channel #moo, manager email placeholder
- [x] 7.2 Create demo setup documentation (in `demo/` or `README.md` section): required steps (#moo channel, manager email), recommended steps (seed emails with templates, calendar standup event), authentication note

## 8. Documentation Review

- [x] 8.1 Read `README.md` and update if necessary
- [x] 8.2 Read `PLANS.md` and update if necessary
- [x] 8.3 Read `AGENTS.md` and update if necessary (demo setup section if it exists)

## 9. Verification

- [x] 9.1 Run `uv run ruff format src/ tests/`
- [x] 9.2 Run `uv run ruff check src/ tests/`
- [x] 9.3 Run `uv run ty check src/`
- [x] 9.4 Run `uv run pytest` — confirm no regressions
