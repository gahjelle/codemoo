# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

> Note to coding agent: Delete questions and tasks from the lists below after
> they're implemented. Propose future tasks in the final section.

## Questions

- Is there a real difference with ReadBot and ScanBot / ChangeBot and SendBot? Should we merge them?
- Should tool output be added to conversation history?
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?
- Can we use raw LLM response to calculate token usage?

## Tasks

- Redo planning of future bots
- Improve save_memory: write in english, don't lose lde memories
- Review all prompts and ~~instructions~~
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Update prompts to "trust the tool"
- Add sessions and store them to disk, include --resume functionality
- Include some information about current context on status bar
- Stream answers

## Proposed by agent
