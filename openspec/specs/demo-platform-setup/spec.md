# Spec: Demo Platform Setup

## Purpose

Defines the pre-demo setup requirements for M365 and Workspace demo paths, including required infrastructure (team channel, template files) and documentation of setup steps.

## Requirements

### Requirement: A team communication channel named `moo` exists before the demo
The M365 and Workspace demo paths include a SendBot prompt that posts to the team channel. This channel SHALL be created manually before running the demo.

For M365, this is a Teams channel named `moo`. For Workspace, this is a Google Chat space named `moo`.

#### Scenario: SendBot posts to the moo channel
- **WHEN** the SendBot prompt "Post to the team channel: I'm back and catching up" is used
- **THEN** the agent SHALL post to a channel/space named `moo` without error

### Requirement: A TEAM.md template exists in the demo/ folder
`demo/TEAM.md` SHALL contain the prebaked team context that GuardBot is asked to create during the demo. This file serves as a reference for the presenter and as the expected output of the GuardBot prompt.

The file SHALL contain:
- Team name: Oomedoc Maet
- Project description referencing Grassroots AI (training cows as an alternative to AI assistants)
- Three team members: Clara, Owen, Wendy
- Standup: Mondays 10:30am
- Channel: #moo
- Communication norms (formal external, casual internal)
- A placeholder for the manager's email address

#### Scenario: Template file exists with expected fields
- **WHEN** `demo/TEAM.md` is read
- **THEN** it SHALL contain team name, project description, member names, standup time, channel name, communication norms, and a manager email placeholder

### Requirement: Demo setup documentation covers required and recommended pre-demo steps
A demo setup document SHALL exist describing what must be configured before running the M365 or Workspace demo path. It SHALL distinguish required steps (demo breaks without them) from recommended steps (demo is richer with them).

Required steps SHALL include:
- Creating the `moo` channel or space
- Having the manager's email address available

Recommended steps SHALL include:
- Seeding 2-3 emails in the inbox (with templates): a client status request, a teammate message needing reply, and one informational email
- Adding a "Team standup" calendar event on Mondays at 10:30am

Authentication SHALL be documented as automatic (triggered on first tool call).

#### Scenario: Setup doc lists the moo channel as required
- **WHEN** the demo setup documentation is read
- **THEN** it SHALL list creating a `moo` Teams channel (M365) or Chat space (Workspace) as a required step

#### Scenario: Setup doc includes seed email templates
- **WHEN** the recommended section of the setup doc is read
- **THEN** it SHALL include at least one email template for a client status request
