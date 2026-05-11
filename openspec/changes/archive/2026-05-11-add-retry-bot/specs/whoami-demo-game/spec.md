## ADDED Requirements

### Requirement: demo/whoami.py is a daily-seeded famous-person guessing game
`demo/whoami.py` SHALL be a standalone Python script that selects a mystery person from a hardcoded list using `random.seed(datetime.date.today().toordinal())`, ensuring the same person is chosen for all invocations on a given calendar day. The list SHALL contain at least 15 people drawn from science, art, history, and technology — diverse in era, background, and gender.

#### Scenario: Same person is selected all day
- **WHEN** `whoami.py` is run multiple times on the same calendar day
- **THEN** the same mystery person SHALL be selected each time

#### Scenario: Person may change on a new calendar day
- **WHEN** `whoami.py` is run on a different calendar day
- **THEN** a different person MAY be selected (seed changes daily)

### Requirement: demo/whoami.py uses MISTAKE_API_KEY — a deliberate typo
`demo/whoami.py` SHALL read its API key from `os.environ["MISTAKE_API_KEY"]` (not `MISTRAL_API_KEY`). This deliberate typo causes a `KeyError` at runtime when the `MISTAKE_API_KEY` variable is not set (which it never is), while `MISTRAL_API_KEY` is set in the demo environment. The typo SHALL NOT be corrected in the source file — it is the intentional failure that RetryBot surfaces.

#### Scenario: Running whoami.py raises KeyError on MISTAKE_API_KEY
- **WHEN** `uv run python whoami.py` is executed in the demo environment
- **THEN** the process SHALL exit with a non-zero return code
- **AND** stderr SHALL contain `KeyError: 'MISTAKE_API_KEY'`

#### Scenario: Fixing the typo to MISTRAL_API_KEY allows the game to run
- **WHEN** `MISTAKE_API_KEY` is replaced with `MISTRAL_API_KEY` in the source
- **THEN** `uv run python whoami.py` SHALL complete successfully and print the mystery guest's introduction

### Requirement: demo/whoami.py makes exactly one LLM call per invocation and exits
`demo/whoami.py` SHALL NOT use `input()` or any interactive loop. Each invocation SHALL make exactly one call to the Mistral API (`mistral-small-latest` via the OpenAI-compatible client at `https://api.mistral.ai/v1`) and then exit. The script is designed to be called repeatedly by a bot's shell tool, not run interactively by a human.

#### Scenario: Script exits after one LLM response
- **WHEN** `whoami.py` completes successfully
- **THEN** exactly one API call SHALL have been made and the process SHALL have exited

### Requirement: demo/whoami.py supports three CLI modes based on sys.argv
The script SHALL behave differently based on the number and content of command-line arguments:

- **No arguments**: The LLM introduces the mystery person in first person without revealing their name. System prompt: `"You are {person}. Never reveal your name or any information that directly identifies you. The user will try to guess who you are. If the user's guess is very close to your name — including minor spelling errors or using only your first or last name — confirm enthusiastically that they have identified you correctly."` User message: `"Introduce yourself without revealing your name."`
- **One argument, no code match**: The argument is passed as a question using the same system prompt. The LLM answers in character, but MAY self-trigger a reveal if the guess is a near-miss (e.g. a typo like "Shakespeer" for Shakespeare).
- **One argument, code match**: At least one word of 4+ characters from `sys.argv[1]` is found as a substring of the person's full name (case-insensitive). The code sends a deterministic reveal prompt: `"The user has guessed your identity correctly. Confirm enthusiastically that you are {person}."` using the same system prompt.

The soft LLM trigger in the system prompt is a fallback for fuzzy matches the code cannot catch (typos, phonetic approximations). The code trigger guarantees a clean reveal for unambiguous guesses.

#### Scenario: No-argument invocation produces an introduction
- **WHEN** `whoami.py` is run with no arguments
- **THEN** stdout SHALL contain a first-person introduction that does not include the person's name

#### Scenario: Question argument produces an in-character answer
- **WHEN** `whoami.py "Were you born before 1900?"` is run
- **THEN** stdout SHALL contain an in-character answer from the mystery guest

#### Scenario: Full name match produces a code-side reveal
- **WHEN** `whoami.py "Are you Marie Curie?"` is run and the mystery person is Marie Curie
- **THEN** `"marie"` or `"curie"` (both ≥ 4 chars) SHALL match in `"marie curie"`
- **AND** the deterministic reveal prompt SHALL be sent to the LLM
- **AND** stdout SHALL contain an enthusiastic confirmation of identity

#### Scenario: Last name only triggers code-side reveal
- **WHEN** `whoami.py "Is it Einstein?"` is run and the mystery person is Albert Einstein
- **THEN** `"einstein"` (≥ 4 chars) SHALL be found as a substring of `"albert einstein"` (case-insensitive)
- **AND** the deterministic reveal prompt SHALL be used

#### Scenario: Short name particles do not trigger spurious reveals
- **WHEN** `whoami.py "What did you do?"` is run and the mystery person is Leonardo da Vinci
- **THEN** `"da"` SHALL NOT trigger the code-side reveal (fewer than 4 characters)
- **AND** the question SHALL be passed to the LLM as a normal in-character query

#### Scenario: Near-miss typo may trigger LLM soft reveal
- **WHEN** `whoami.py "Are you Shakespeer?"` is run and the mystery person is William Shakespeare
- **THEN** `"shakespeer"` SHALL NOT match `"william shakespeare"` on the code side
- **AND** the argument SHALL be passed as a question with the regular system prompt
- **AND** the LLM MAY confirm the identity based on the near-miss soft trigger in the system prompt
