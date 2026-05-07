# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

> Note to coding agent: Delete questions and tasks from the lists below after
> they're implemented. Propose future tasks in the final section.

## Questions

- Should tool output be added to conversation history?
- Can we control shell scripts to only touch session folder
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?
- Can we use raw LLM response to calculate token usage?

## Tasks

- Only read project context at startup
- Review all prompts and instructions
- Improve system prompts. Add in a bit of character in bots after Sona (but scaled back from Sona itself)
- Introduce concept of session folder
- Read file-tool locked to session folder
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Update prompts to "trust the tool"
- Add sessions and store them to disk, include --resume functionality
- Include some information about current context on status bar
- Stream answers

## Proposed by agent
