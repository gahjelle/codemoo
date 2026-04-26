## 1. Create demo/ artifacts

- [x] 1.1 Create `demo/names.txt` with the nine bot names and emojis (Coco 🦜 through Cato 🔒), one per line
- [x] 1.2 Create `demo/greeter.py` with `load_names()` (encoding="ascii" bug), `greet()`, and `main()`; full type annotations and module docstring
- [x] 1.3 Create `demo/test_greeter.py` with pytest tests that import `load_names` and `greet` from `greeter` directly and assert on their return values
- [x] 1.4 Create `demo/README.md` describing the greeter project; include the claim that "names are sorted alphabetically" (intentional inaccuracy)
- [x] 1.5 Verify: `python demo/greeter.py` crashes with `UnicodeDecodeError`
- [x] 1.6 Verify: `uv run pytest demo/test_greeter.py` fails (before fix)
- [x] 1.7 Verify: fixing `encoding="ascii"` → `encoding="utf-8"` makes `uv run pytest demo/test_greeter.py` pass, then revert to keep bug in place

## 2. Update demo prompts in configs/codemoo.toml

- [x] 2.1 Replace FileBot prompts with the four new prompts (read greeter.py, write review.txt, compare README+greeter, read archive.txt)
- [x] 2.2 Replace ShellBot prompts with the four new prompts (run greeter.py, run pytest, compare README+greeter via cat, count names)
- [x] 2.3 Replace AgentBot prompts with the two new prompts (which tools, fix the crash)
- [x] 2.4 Replace GuardBot prompts with the three new prompts (which tools require approval, write summary.md, run tests then commit)

## 3. Update documentation

- [x] 3.1 Update the `### Demo Arc` section in `BOTS.md`: mark Acts 1–4 as implemented, add planned Acts 5–10 covering all remaining bots (Lore through Codemoo)
- [x] 3.2 Add a working-directory note to the Demo Mode section of `README.md`: instruct users to `cd demo` before running `uv run codemoo demo`
- [x] 3.3 Update the bot progression table in `README.md` to include GuardBot (🔒 Cato)
- [x] 3.4 Add a "Demo Environment" section to `AGENTS.md` documenting that `demo/greeter.py`'s `encoding="ascii"` and `demo/README.md`'s sorting claim are intentional and must not be fixed

## 4. Verification

- [x] 4.1 Run `uv run ruff check .` and `uv run ruff format .` — no errors
- [x] 4.2 Run `uv run ty check .` — no errors
- [x] 4.3 Run `uv run pytest` — all existing tests pass
- [x] 4.4 Run `uv run codemoo demo` from `demo/` and manually step through Rune → Ash → Loom → Cato prompts to confirm the narrative arc works end-to-end
