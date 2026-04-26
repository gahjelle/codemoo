## Why

Demo prompts in Acts 3–4 (Rune, Ash, Loom, Cato) reference whatever happens to be in the project at the time — AGENTS.md, src/ Python files, randomly-sized Markdown files — making them fragile and narratively disconnected. A self-contained `demo/` folder with purpose-built artifacts lets Acts 3–4 tell a single coherent story the presenter can rely on every time.

## What Changes

- **New `demo/` folder** with four files: a buggy greeter script (`greeter.py`), its tests (`test_greeter.py`), input data (`names.txt`), and a description (`README.md`)
- **Revised prompts** for FileBot, ShellBot, AgentBot, and GuardBot in `configs/codemoo.toml` — paths are relative to `demo/` (the intended working directory)
- **Updated demo arc** in `BOTS.md` — adds GuardBot to Act 4, expands planned acts to cover all 23 bots
- **Working-directory note** added to `README.md` explaining that demo prompts expect `demo/` as the working directory

## Capabilities

### New Capabilities

- `demo-artifacts`: The `demo/` folder and its contents — a self-contained greeter project used as the subject of Acts 3–4 demo prompts

### Modified Capabilities

- `demo-preset-prompts`: Prompt content for FileBot, ShellBot, AgentBot, and GuardBot changes to reference `demo/` artifacts; the working-directory assumption is now explicit

## Impact

- `demo/` folder (new): four new files added to the repository
- `configs/codemoo.toml`: prompts updated for FileBot, ShellBot, AgentBot, GuardBot
- `BOTS.md`: demo arc section rewritten
- `README.md`: one paragraph added to the Demo Mode section
- `AGENTS.md`: new "Demo Environment" section documenting intentional issues in `demo/`
- No bot implementation code changes; no new bots; no TUI or slide changes

## Non-goals

- Changing any bot implementation code
- Adding new bots or bot types
- Changing TUI layout or demo slide content
- Updating prompts for EchoBot, LlmBot, ChatBot, SystemBot, or ToolBot
