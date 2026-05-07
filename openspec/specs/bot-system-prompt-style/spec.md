# Spec: bot-system-prompt-style

## Purpose

TBD — defines the canonical four-part structure that all bot system prompt instruction files (from Telo onwards) must follow: identity, capability, behavior trigger, and credo. Establishes per-bot credo conventions and length guidelines for code versus platform variants.

## Requirements

### Requirement: Bot system prompts follow a four-part form
Every bot system prompt from Telo onwards SHALL follow a four-part structure in order: (1) identity, (2) capability, (3) behavior trigger, (4) credo. No section SHALL be omitted. The identity line SHALL always read `You are [Name], a [role].` The credo SHALL always be the final sentence.

#### Scenario: Identity line uses correct role token
- **WHEN** a bot instruction file is authored for a code variant
- **THEN** the identity line SHALL read `You are [Name], a coding assistant.`
- **AND** SHALL NOT include an adjective prefix such as "helpful" or "business"

#### Scenario: Platform variant uses productivity assistant role
- **WHEN** a bot instruction file is authored for an M365 or Workspace variant
- **THEN** the identity line SHALL read `You are [Name], a productivity assistant.`

#### Scenario: Credo is the final sentence
- **WHEN** a bot instruction file is authored
- **THEN** the credo SHALL appear as the last sentence of the prompt

### Requirement: Each bot has a canonical credo
Each bot from Telo to Lore SHALL have a canonical credo that captures its operating principle. The credo text SHALL be identical across all variants of that bot. Only domain vocabulary within the body of the prompt adapts per variant.

#### Scenario: Credo is consistent across code and platform variants
- **WHEN** the same bot has both a code variant and a platform variant
- **THEN** the final credo sentence SHALL be word-for-word identical in both instruction files

### Requirement: Platform variant instruction files list available API tools
Platform (M365 and Workspace) variant instruction files SHALL include one sentence listing the specific API tools available to that bot (e.g. "You can read email, access SharePoint, create calendar events, and post to Teams."). Code variant instruction files SHALL NOT enumerate tools — the tool config is the capability declaration.

#### Scenario: Code variant does not list tools
- **WHEN** a code variant instruction file is authored
- **THEN** it SHALL NOT contain a sentence enumerating specific tool names such as read_file or run_shell

#### Scenario: Platform variant lists domain tools
- **WHEN** an M365 or Workspace variant instruction file is authored
- **THEN** it SHALL contain a sentence naming the platform-specific tools available to that variant

### Requirement: Code variants run to approximately three sentences
Code variant instruction files SHALL be approximately three sentences in length — one for each of: capability/behavior, tool trigger, and credo. The identity line is not counted.

#### Scenario: Code variant instruction file length
- **WHEN** a code variant instruction file is authored
- **THEN** it SHALL contain approximately three sentences after the identity line

### Requirement: Platform variants run to approximately four sentences
Platform variant instruction files SHALL be approximately four sentences in length — capability/behavior, tool listing, tool trigger, and credo. The identity line is not counted.

#### Scenario: Platform variant instruction file length
- **WHEN** a platform variant instruction file is authored
- **THEN** it SHALL contain approximately four sentences after the identity line
