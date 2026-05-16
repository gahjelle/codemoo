## 1. Schema: PersonaConfig and CodemooConfig

- [x] 1.1 Add `PersonaConfig` model to `src/codemoo/config/schema.py` with fields `name`, `emoji` (resolved via `resolve_emoji` validator), `instructions`, `instructions_file`
- [x] 1.2 Add `commentators: dict[str, PersonaConfig]` field to `CodemooConfig` in `src/codemoo/config/schema.py` (keyed by TOML table key, consistent with `bots` and `scripts`)
- [x] 1.3 Update the config loader to resolve `instructions_file` references for each `PersonaConfig` by reading from `src/codemoo/config/commentators/<filename>`

## 2. Config Files: codemoo.toml and commentators/ folder

- [x] 2.1 Create `src/codemoo/config/commentators/` folder
- [x] 2.2 Write `arne.txt` — sage elder, Gandalf-like, measured wisdom, lets moments breathe
- [x] 2.3 Write `herwig.txt` — flowery, rhymes and alliteration (migrate existing instructions)
- [x] 2.4 Write `solve.txt` — dry, deadpan, terse (migrate existing instructions)
- [x] 2.5 Write `rike.txt` — skeptical, secretly impressed (migrate existing instructions)
- [x] 2.6 Write `unni.txt` — excited athlete-commentator, handball insider credibility (based on Unni Anisdahl)
- [x] 2.7 Write `th.txt` — warm, witty, charming, finds comedy in everything (based on Knut Th. Gleditsch)
- [x] 2.8 Write `karen-marie.txt` — pioneer authority, precise, unflappable (based on Karen-Marie Ellefsen)
- [x] 2.9 Write `bjornsen.txt` — comments only as unanswered quiz questions (based on Knut Bjørnsen)
- [x] 2.10 Write `bredeli.txt` — makes outlandish bets in every comment (based on Harald Bredeli)
- [x] 2.11 Write `jorsett.txt` — obsessed with measurable outcomes and comparisons (based on Per Jorsett)
- [x] 2.12 Add all ten `[commentators.<key>]` entries to `src/codemoo/config/codemoo.toml` (e.g. `[commentators.arne]`) with correct `name`, `emoji`, and `instructions_file` values

## 3. CommentatorBot Refactor

- [x] 3.1 Add `personas: list[Persona]` as a required dataclass field to `CommentatorBot` in `src/codemoo/core/bots/commentator_bot.py`
- [x] 3.2 Remove the `_PERSONAS` module-level list from `commentator_bot.py`
- [x] 3.3 Update `_generate_comment()` to draw from `self.personas` instead of `_PERSONAS`; guard against empty list by falling back to Streik
- [x] 3.4 Update `sender_info()` to iterate `self.personas` instead of the hardcoded list

## 4. tui.py Construction Sites

- [x] 4.1 Update `code_chat` in `src/codemoo/frontends/tui.py` to pass `personas=list(config.commentators.values())` when constructing `CommentatorBot`
- [x] 4.2 Update `business_chat` in `src/codemoo/frontends/tui.py` similarly
- [x] 4.3 Update `demo` in `src/codemoo/frontends/tui.py` similarly

## 5. Tests

- [x] 5.1 Update `tests/core/bots/test_commentator_bot.py` to construct `CommentatorBot` with an explicit `personas` list
- [x] 5.2 Remove or update any test that asserts exactly four personas or checks for hardcoded persona names (Arne, Herwig, Sølve, Rike as the complete set)
- [x] 5.3 Add a test that `sender_info()` returns keys for all personas passed in plus `Streik`
- [x] 5.4 Add a test that `CommentatorBot` with `personas=[]` falls back to Streik on `comment()` call

## 6. Verification

- [x] 6.1 Run `uv run ruff check src/ tests/` and fix any issues
- [x] 6.2 Run `uv run ruff format src/ tests/`
- [x] 6.3 Run `uv run ty check src/ tests/` and fix any issues
- [x] 6.4 Run `uv run pytest` and confirm all tests pass

## 7. Documentation

- [x] 7.1 Read `AGENTS.md` and update if necessary (commentator architecture section)
- [x] 7.2 Read `BOTS.md` and update if necessary
- [x] 7.3 Read `README.md` and update if necessary
- [x] 7.4 Read `PLANS.md` and update if necessary
