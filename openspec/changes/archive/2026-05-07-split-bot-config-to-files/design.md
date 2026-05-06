## Context

`codemoo.toml` (444 lines) is the single source of truth for all bot configuration. The bulk is bot variant entries containing multi-line `instructions` strings and `prompts` lists. The current loading chain in `config/__init__.py` is a simple fluent call: `Configuration.from_file() → .add_envs() → .parse_dynamic() → .convert_model(CodemooConfig)`. The `Configuration` type from configaroo is a `UserDict` with a `.data` dict attribute holding the raw TOML parse result.

No downstream code — bots, TUI, demo scripts — consumes raw TOML values; everything goes through `ResolvedBotConfig` produced by `resolve()`. The schema types `BotVariantConfig.instructions: str` and `BotVariantConfig.prompts: list[str]` are the contract that must be preserved.

## Goals / Non-Goals

**Goals:**
- Allow `instruction_file` and `prompts_file` keys in bot variant TOML entries as alternatives to inline values
- Resolve file references to strings before Pydantic validation, leaving schema unchanged
- Reduce `codemoo.toml` verbosity; make individual instruction and prompt files easy to open during demos
- Support both inline and file-based values simultaneously (neither is mandatory)

**Non-Goals:**
- Changing `BotVariantConfig`, `CodemooConfig`, or any other schema type
- Splitting `codemoo.toml` into per-bot files
- Any changes to bot implementations, TUI, or demo scripts

## Decisions

### Resolution happens in the loader, not in a Pydantic validator

File references are resolved in a `_resolve_file_refs(data: dict) -> None` function that mutates the raw TOML dict before `Configuration.from_dict()` is called. Pydantic never sees `instruction_file` or `prompts_file` keys.

**Why not a Pydantic `model_validator`?**
- Validators doing I/O are an antipattern: `FileNotFoundError` surfaces as a confusing `ValidationError`, validators may run multiple times, and `BotVariantConfig` would become untestable without files on disk
- The validator would need to hardcode the instructions directory path relative to `schema.py`, coupling schema to filesystem layout
- The loader already knows `config_path`, so the directory derivation is natural there

**Alternatives considered:**
- `model_validator(mode="before")` on `BotVariantConfig` — rejected (see above)
- Post-processing after `convert_model()` — rejected because `CodemooConfig` and `BotVariantConfig` are frozen Pydantic models; mutating them after construction requires re-instantiation

### `---` on its own line as the prompt separator

Prompts in `.txt` files are separated by a line containing only `---`. Parsed with `re.split(r"^\-{3}$", content, flags=re.MULTILINE)`, strips leading/trailing whitespace from each segment.

**Why not `\n\n`?** Blank lines within a prompt (e.g. multi-paragraph task descriptions like the GuardBot Streamlit challenge) would silently split one prompt into two. `---` is unambiguous and visually clear in an editor.

**Why not one-per-line?** The GuardBot Streamlit prompt is already multi-sentence and multi-line.

### File naming convention: `{bot_type_snake}-{variant}.txt`

Examples: `system_bot-default.txt`, `guard_bot-code.txt`, `agent_bot-m365.txt`.

Snake-case maps directly from the TOML bot key (e.g. `SystemBot` → `system_bot`). The variant name appended after `-` makes the file self-describing. Files are not auto-discovered; the TOML entry explicitly names the file via `instruction_file` or `prompts_file`.

### Directory layout

```
src/codemoo/config/
  codemoo.toml
  instructions/          ← system prompt text files
  example_prompts/       ← prompt list text files
```

Both directories are siblings of `codemoo.toml`. The loader derives their paths as `config_path.parent / "instructions"` and `config_path.parent / "example_prompts"`, so no new config keys are needed.

### Inline values remain fully supported

Bots with short or empty `instructions` (EchoBot, LlmBot, ChatBot) keep their inline values (or omit the field entirely). The loader only triggers file resolution when `instruction_file` / `prompts_file` keys are present; it leaves `instructions` / `prompts` untouched when inline.

## Risks / Trade-offs

**Missing file → startup crash** — If `instruction_file = "foo.txt"` is set but the file doesn't exist, `Path.read_text()` raises `FileNotFoundError` at import time. This is a loud, obvious failure (not a silent wrong value), which is acceptable. The error message from Python is clear enough; no additional wrapping is added.

**`---` in prompt content** — A prompt that contains a line of exactly `---` would be incorrectly split. This is considered an acceptable constraint given the expected content (short chat prompts). A comment in the example_prompts files can document this.

**File encoding** — All files are read with `Path.read_text()` (system default encoding). An explicit `encoding="utf-8"` call prevents surprises on Windows. Should be applied in `_resolve_file_refs`.

## Open Questions

(none — all design decisions resolved during exploration)
