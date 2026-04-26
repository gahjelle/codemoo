## Context

Demo prompts for Acts 3–4 currently reference project files (AGENTS.md, src/) whose content and size change as the project evolves. This makes prompts fragile — a "count Python files in src/" prompt gives different answers after adding a file — and the prompts feel unrelated to each other, with no narrative thread.

The fix is to add a `demo/` folder containing a small, stable greeter project that all four bots (Rune, Ash, Loom, Cato) work with in sequence. Acts 3–4 then tell one story: observe the bug → confirm it → fix it → commit it.

## Goals / Non-Goals

**Goals:**
- A `demo/` folder whose contents are fully under our control and will not drift
- A single narrative thread connecting Rune → Ash → Loom → Cato
- Prompts that demonstrate each bot's specific capability *and* its limitation
- Running the demo from `demo/` as working directory so paths in prompts are short and natural

**Non-Goals:**
- Changing how any bot works (no code changes)
- Creating a general-purpose project template; `demo/` is demo-specific
- Making the greeter script a real, production-quality tool

## Decisions

### The bug: `encoding="ascii"` on a file containing emoji

The greeter reads `names.txt` with `encoding="ascii"`. Since `names.txt` contains emoji characters, this crashes immediately with `UnicodeDecodeError: 'ascii' codec can't decode byte 0xf0`.

**Why this bug over alternatives:**
- *Visual*: the error output is unmistakeable and the fix is a one-word change
- *Relatable*: encoding bugs are infamous; every developer has hit one
- *Thematic*: `names.txt` contains the bot names and emojis from the demo itself — the script is trying to greet the very bots the audience just met, and it can't even read their names

Alternatives considered:
- *IndexError (off-by-one)*: dramatic crash but the cause is more mechanical, less story-rich
- *Wrong reversal order*: connects to Act 1 theme but no crash, harder to see in output
- *Missing `()` on method call*: very visual but Python-specific; loses non-Python audiences

### `names.txt` uses the actual bot names and emojis

The nine lines mirror the bot roster shown in the demo slides. This is intentional: the audience recognises these names, making the failure feel personal ("it can't even read Coco's name").

### `demo/README.md` contains one deliberate inaccuracy

README claims "names are sorted alphabetically." The code does not sort. This makes the Rune prompt "Compare README.md and greeter.py — do they match?" reveal a real discrepancy, rather than just confirming everything is consistent.

### Working directory is `demo/`

Prompts reference `greeter.py`, `README.md`, etc. — no `demo/` prefix. This keeps prompts short and natural, and means `cat README.md greeter.py` (the Ash multi-file trick) is idiomatic.

The trade-off: users must `cd demo` before running the demo. This is documented in `README.md` and in `BOTS.md`.

`uv run codemoo demo` still works from `demo/` because `uv` walks up the directory tree to locate `pyproject.toml`.

### GuardBot's approval trigger: `git commit`

Cato's most dramatic prompt ends with committing changes via `git`. This uses `run_shell`, which has `requires_approval=True`, so the approval modal fires on the commit step.

**Why `git commit` over other destructive actions:**
- *Relatable*: developers immediately understand why you'd want a human to approve a commit
- *Visible impact*: commits affect the shared repository history — exactly the kind of action worth pausing for
- `write_file` also triggers approval (it is also `requires_approval=True`), so an earlier prompt ("write a summary to summary.md") demonstrates that approval, and the commit is the escalation

### Rune's two-prompt read → write sequence

Rune gets one tool call per conversation turn. The first prompt reads `greeter.py`; the second asks for a code review written to `review.txt`. Because Rune is ChatBot-based, the greeter content from turn 1 remains in history, so turn 2 can call `write_file` without needing to re-read. This incidentally shows the audience that Rune has conversation memory.

### Ash's `cat` trick contrasts with Rune's limitation

Rune's third prompt ("Compare README.md and greeter.py") reads only one file — the single-tool-call limitation. Ash gets the same prompt and runs `cat README.md greeter.py`, reading both in one shell command. This contrast is the clearest possible demonstration of why shell access is more powerful — and more dangerous.

## Risks / Trade-offs

`demo/test_greeter.py` imports `load_names` and `greet` from `greeter` directly. pytest adds the test file's directory to `sys.path`, so the import works when running `uv run pytest test_greeter.py` from `demo/`.

After Loom fixes `greeter.py`, the file is modified on disk. Cato's prompt ("fix any remaining issues, run tests, commit") works whether or not Loom ran first: if the bug is already fixed, tests pass and Cato proceeds to the commit step. If Loom did not run, Cato fixes the bug itself before committing.

The git commit at the end of the Cato sequence will modify the repository. Presenters should note this and run `git checkout demo/` between demo sessions to reset the state.

## Open Questions

None — all decisions resolved during exploration phase.
