# Commentator Configuration

## Declaring Personas

Commentator personas are declared in `codemoo.toml` under `[commentators.<key>]`:

```toml
[commentators.arne]
name = "Arne"
emoji = "OWL"
instructions_file = "arne.txt"
```

Instruction files live in `src/codemoo/config/commentators/`. File naming convention: `{lowercase-key}.txt` (e.g. `arne.txt`, `karen-marie.txt`). Inline `instructions = "..."` is also supported.

## CommentatorBot

`CommentatorBot` receives `personas: list[Persona]` and `templates: dict[str, str]` at construction. It holds no hardcoded personas or prompt strings. The TUI constructs it with `personas=list(config.commentators.values())` and `templates=dict(config.commentary_templates)`. All personas are selected with uniform random weight.

## Commentary Templates

Event prompt templates are declared in `codemoo.toml` under `[commentary_templates]` and loaded from `src/codemoo/config/commentary_templates/`. Templates use `str.format()` placeholders: `{bot_name}`, `{tool_name}`, `{sig}`, `{detail}`, `{source_desc}`, `{path}`, `{content_len}`, `{preview}`.

Template keys: `"call"`, `"blocked"`, `"error"`, `"context"`, `"memory"`.

## Personas

| Name        | Based on                                                             | Character                                     |
| ----------- | -------------------------------------------------------------------- | --------------------------------------------- |
| Arne        | Arne Scheie (NRK football & ski jumping, 1971–2013)                  | Sage elder — measured, Gandalf-like authority |
| Herwig      | Jon Herwig Carlsen (NRK biathlon, known for live limericks)          | Flowery — rhymes and alliteration             |
| Sølve       | Sølve Grotmol (NRK sports & news, 1960s–2010)                        | Deadpan — terse, unimpressed                  |
| Rike        | Kjell Kristian Rike (NRK biathlon, partner of Carlsen)               | Skeptical — secretly impressed                |
| Unni        | Unni Anisdahl (NRK handball, 72 Norway caps)                         | Excited athlete — insider credibility         |
| Th          | Knut Th. Gleditsch (NRK football & alpine, 1966–2001)                | Warm and witty — charming, light-hearted      |
| Karen Marie | Karen-Marie Ellefsen (first female NRK sports reporter, 10 Olympics) | Pioneer authority — precise, unflappable      |
| Bjørnsen    | Knut Bjørnsen (NRK speed skating; quiz host)                         | Quiz questions only — never answered          |
| Bredeli     | Harald Bredeli (TV2 handball)                                        | Outlandish bets on every moment               |
| Jorsett     | Per Jorsett (NRK speed skating, alongside Bjørnsen)                  | Measurable outcomes and comparisons           |
