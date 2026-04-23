## 1. Update LLM Prompts

- [x] 1.1 In `_build_llm_prompt()` (first-bot variant), replace "Don't use Markdown" with an instruction to use Markdown and include a fenced code block for the key line(s)
- [x] 1.2 In `_build_llm_prompt()` (subsequent-bot variant), replace "Don't use Markdown" with the same Markdown instruction

## 2. Verify Rendering

- [ ] 2.1 Run `uv run codemoo --demo` and confirm the slide "What's new" section renders with syntax-highlighted code block
- [ ] 2.2 Confirm output still fits on screen (no runaway length)
