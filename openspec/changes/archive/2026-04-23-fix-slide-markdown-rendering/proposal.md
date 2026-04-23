## Why

The demo slide's "What's new" section uses a Textual `Markdown` widget but the LLM prompt explicitly says "Don't use Markdown", so responses are plain text that bypasses the renderer entirely. Audiences see unformatted walls of text when they should see nicely structured explanations with code blocks.

## What Changes

- Remove "Don't use Markdown" instruction from both LLM prompt variants in `slides.py`
- Replace it with an explicit instruction to use Markdown, including fenced code blocks for key code snippets
- Adjust prompt guidance so the LLM produces well-structured output (short prose + one code block) that fits on screen

## Capabilities

### New Capabilities
<!-- None — this is a prompt fix, not a new capability -->

### Modified Capabilities
- `demo-slide-screen`: The LLM-generated "What's new" explanation requirement changes — it SHALL now be Markdown-formatted with at least one fenced code block, and the `Markdown` widget SHALL render it as rich text

## Impact

- `src/codemoo/chat/slides.py` — `_build_llm_prompt()` function only
- No widget changes required; `Markdown` widget already handles rendering
- No test changes unless snapshot tests capture raw LLM output (they don't — LLM is mocked or excluded)
