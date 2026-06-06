# Platform Demo Setup

This file covers what to configure before running the M365 or Workspace demo
paths (the bots from ScanBot through MemoryBot on the platform variants).

---

## Required

These steps are necessary for the demo to run without errors.

- **Create a `moo` channel/space**
  - M365: create a Teams channel named `moo`
  - Workspace: create a Google Chat space named `moo`

- **Know your manager's email address**
  GuardBot will ask for it during the demo before writing TEAM.md. Have it
  ready to type in when prompted.

---

## Recommended

These steps make the demo richer. The prompts work without them, but a sparse
inbox produces less interesting output.

- **Seed your inbox with 2-3 emails** — send these to yourself before the demo:

  **Email 1 — client status request (use this for the GuardBot reply)**
  > Subject: Project status update?
  >
  > Hi,
  >
  > Hope you had a good break. Just checking in — could you send over a quick
  > status update on the Grassroots AI project when you get a chance?
  >
  > Thanks,
  > A. Stakeholder

  **Email 2 — teammate message**
  > Subject: Quick question
  >
  > Hey, welcome back! When you have a moment, can you review the notes from
  > Monday's standup? I left a few open items that need your input.
  >
  > — Owen

  **Email 3 — informational, no reply needed**
  > Subject: Team offsite confirmed
  >
  > Just a heads up — the offsite date has been confirmed for next month.
  > Calendar invite to follow.

- **Add a standing calendar event**
  Create a recurring event: "Team standup" — Mondays at 10:30am.
  This matches the TEAM.md content and makes the calendar scan more realistic.

---

## Authentication

Authentication is handled automatically. The first time a platform tool is
called, the app triggers OAuth for M365 or Google Workspace. No pre-configuration
is needed.

---

## Reference: TEAM.md Content

GuardBot creates this file during the demo. The reference version is at
`demo/TEAM.md`. The only field the agent asks for interactively is the
manager's email address — everything else is prebaked into the prompt.