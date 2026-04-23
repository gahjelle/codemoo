## Context

The slide's "What's new" section uses Textual's `Markdown` widget (which renders rich text), but the LLM prompts in `_build_llm_prompt()` end with "Don't use Markdown." This forces the LLM to produce plain prose, wasting the renderer.

The fix is entirely in `_build_llm_prompt()` — two string literals, no widget or data-model changes.

## Goals / Non-Goals

**Goals:**
- LLM returns Markdown-formatted explanations with fenced code blocks
- `Markdown` widget renders them as intended (syntax-highlighted code, bold/italic emphasis)
- Prompt still constrains output length to fit on screen

**Non-Goals:**
- Changing widget layout or adding new widgets
- Modifying `slides_data.py` bot descriptions (plain text, displayed in `Label`)
- Adding Markdown rendering to the title or description `Label` widgets

## Decisions

**Update the prompt instruction strings only.**

Both prompt variants (first bot and subsequent bots) end with a plain-English instruction that currently says "Don't use Markdown." Replace with "Use Markdown. Show key code in a fenced code block."

Alternative considered: replace all `Label` widgets with `Markdown` widgets throughout the slide so the title and description could also be Markdown. Rejected — those strings are static and short; `Label` is simpler and appropriate there.

## Risks / Trade-offs

- [Risk] LLM output may be longer when it uses headers and code blocks → Mitigation: Prompt still says "5–8 lines" and "must fit on a single screen"; code blocks add vertical space but the Textual `Markdown` widget scrolls if needed.
- [Risk] Some LLMs ignore formatting instructions and produce too much Markdown → Mitigation: Prompt is explicit about structure ("one fenced code block, short prose above it").
