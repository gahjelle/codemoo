## 1. Schema and TOML

- [x] 1.1 Extend `BotType` Literal in `schema.py` to all 8 class names; remove `BotModule` type alias
- [x] 1.2 Remove `type` field from `BotConfig`; add `emoji` field validator using `unicodedata.lookup()`
- [x] 1.3 Change `CodemooConfig.bots` to `dict[BotType, BotConfig]`
- [x] 1.4 Add remaining 6 bots to `configs/codemoo.toml`, keyed by class name, with name/emoji/description/sources

## 2. FC/IS: Language injection

- [x] 2.1 Add `language: str = "English"` field to `ErrorBot`; remove `config` import; use `self.language` in prompts
- [x] 2.2 Add `language: str = "English"` field to `CommentatorBot`; remove `config` import; use `self.language` in prompts
- [x] 2.3 Pass `language=config.language` to `ErrorBot` and `CommentatorBot` in `tui.py._setup()`

## 3. make_bots()

- [x] 3.1 Update `make_bots()` in `core/bots/__init__.py` to read `name` and `emoji` from `config.bots[ClassName]` for each of the 8 bots

## 4. slides.py and slides_data.py

- [x] 4.1 Replace `_BOTS_DIR` constant with `config.paths.bots_dir` in `slides.py`; remove `Path` import if no longer needed
- [x] 4.2 Replace `BOT_SOURCES.get(...)` with `config.bots.get(type(bot).__name__)` lookup in `_bot_source_block()`
- [x] 4.3 Replace `BOT_DESCRIPTIONS.get(...)` with config lookup in `SlideContent.compose()`
- [x] 4.4 Remove `from codemoo.chat.slides_data import BOT_DESCRIPTIONS, BOT_SOURCES` import from `slides.py`
- [x] 4.5 Delete `src/codemoo/chat/slides_data.py`

## 5. Test cleanup

- [x] 5.1 Delete `tests/test_config.py`
- [x] 5.2 Update `tests/core/bots/test_error_bot.py`: remove `language_instruction` import; update `test_format_error_passes_instructions_to_backend` to check `"Answer in English"` in the system message
- [x] 5.3 Run full test suite and fix any remaining failures

## 6. Verification

- [x] 6.1 Run `uv run ruff check .` and `uv run ruff format .`; fix any issues
- [x] 6.2 Run `uv run ty check .`; fix any type errors
- [x] 6.3 Review `README.md` for references to `language_instruction`, `CODEMOO_LANGUAGE` env var usage, bot names/emojis, or config instructions that need updating
