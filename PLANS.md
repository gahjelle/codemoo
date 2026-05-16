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
- Add shell mode to manually call run_shell
- Maybe include a file mode to manually read files? Not really necessary, since we have !cat
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Update prompts to "trust the tool"
- Add sessions and store them to disk, include --resume functionality
- Add num tokens in context visibly on screen
- Stream answers
- Show full content of first parameter in GuardBot approval box
- Add context management capability that can customize context
- Add tool management capability that can customize tools
- Run all tool calls in one turn, not only the first one

## Proposed by agent
