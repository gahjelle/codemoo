## ADDED Requirements

### Requirement: RetryBot code variant has three preset prompts demonstrating retry and escalation
The file `src/codemoo/config/example_prompts/retry_bot-code.txt` SHALL contain exactly three prompts separated by `---`:

1. A numpy availability check (`uv run python -c 'import numpy'`) — a standalone prompt requiring no prior demo state that fails consistently with `ModuleNotFoundError` and demonstrates the retry-then-escalate mechanism.
2. A whoami game run (`uv run python whoami.py`) — fails consistently with `KeyError: MISTAKE_API_KEY`, demonstrates retry on a realistic tool failure, and escalates with a useful diagnosis.
3. A fix-and-rerun prompt (`Fix the variable name in whoami.py and run the game again.`) — reads the file, patches `MISTAKE_API_KEY` → `MISTRAL_API_KEY`, and runs the game successfully to produce the mystery guest introduction.

#### Scenario: First prompt demonstrates retry on zero setup
- **WHEN** the first preset prompt is submitted to RetryBot in a fresh session
- **THEN** the bot SHALL attempt the numpy import 3 times and escalate with `ModuleNotFoundError`

#### Scenario: Second prompt demonstrates retry on API key failure
- **WHEN** the second preset prompt is submitted after the demo environment is set up
- **THEN** the bot SHALL attempt to run whoami.py 3 times and escalate with a `KeyError: MISTAKE_API_KEY` diagnosis

#### Scenario: Third prompt results in a successful game run
- **WHEN** the third preset prompt is submitted after the second has escalated
- **THEN** the bot SHALL fix the typo in whoami.py and run it successfully, printing the mystery guest's introduction

### Requirement: RetryBot m365 variant has prompts demonstrating retry on missing resources
The file `src/codemoo/config/example_prompts/retry_bot-m365.txt` SHALL contain prompts that reliably trigger repeated tool failures against non-existent M365 resources. At minimum: an attempt to read an email with subject containing "Q3 Board Report" (no such email exists) and an attempt to read a SharePoint document named "Strategy2030.docx" (no such file exists). Both SHALL return `Error 4xx` responses on each attempt, triggering escalation.

#### Scenario: Missing email read triggers retry and escalation
- **WHEN** the m365 preset prompt to read the Q3 Board Report email is submitted
- **THEN** the bot SHALL attempt the read 3 times and escalate with the 404/not-found error

### Requirement: RetryBot workspace variant has prompts demonstrating retry on missing resources
The file `src/codemoo/config/example_prompts/retry_bot-workspace.txt` SHALL contain analogous prompts targeting Gmail and Google Drive. At minimum: an attempt to find an email about "Q3 Board Report" and an attempt to read a Drive file named "Strategy2030.docx".

#### Scenario: Missing Drive file read triggers retry and escalation
- **WHEN** the workspace preset prompt to read Strategy2030.docx is submitted
- **THEN** the bot SHALL attempt the read 3 times and escalate with the not-found error
