## ADDED Requirements

### Requirement: demo/whoami.py exists with the deliberate MISTAKE_API_KEY typo
`demo/whoami.py` SHALL be present in the repository at all times (not generated during a demo run). It SHALL use `os.environ["MISTAKE_API_KEY"]` — a deliberate typo. The file SHALL NOT be corrected. It is the pre-seeded failure artifact for the RetryBot demo, analogous to `demo/greeter.py`'s `encoding="ascii"` bug.

#### Scenario: whoami.py is present in the demo directory
- **WHEN** the repository is checked out
- **THEN** `demo/whoami.py` SHALL exist

#### Scenario: whoami.py fails at runtime due to the typo
- **WHEN** `uv run python whoami.py` is executed in the demo environment
- **THEN** a `KeyError: 'MISTAKE_API_KEY'` SHALL be raised, because that variable is never set
