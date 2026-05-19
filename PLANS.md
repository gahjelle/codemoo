# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

> Note to coding agent: Delete questions and tasks from the lists below after
> they're implemented. Propose future tasks in the final section.

## Questions

- Is there a real difference with ReadBot and ScanBot / ChangeBot and SendBot? Should we merge them?
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?
- Can we use raw LLM response to calculate token usage?

## Tasks

- Improve save_memory: write in english, don't lose old memories
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Make tool calls async and update the loop to use asyncio.gather()
- Update prompts to "trust the tool"
- Add sessions and store them to disk, include --resume functionality
- Stream answers
- Show full content of first parameter in GuardBot approval box
- Add context editing capability: select, disable, summarise, or edit individual context items via a modal UI (the read-only inspector from `context_display` is the foundation)
- Add tool management capability that can customize tools
- Move compaction limit to config. Use a small window on CompactBot (demo), but a bigger (100k?) on other bots, including the codemoo variant.

## Proposed by agent

- Include system message tokens in the `context_management` status bar count — currently `estimate_tokens(build_context(_chat_context))` excludes the system prompt (instructions + project context + memory), which is fixed overhead that still consumes the context window. The cleanest fix is to have `startup()` push a `SystemContent` ContextItem so `build_context` picks it up automatically.
