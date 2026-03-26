# Claude Code Setup

Custom hooks, agents, skills, and rules for Claude Code.

## Structure

```
├── agents/          # 5 specialized agents
├── hooks/           # Python lifecycle hooks with local TTS
├── skills/          # Art, Learnings, Writing, PDF, Remotion
├── rules/           # Code style enforcement
├── commands/        # Custom slash commands
└── settings.json    # Hook configuration
```

## Agents

| Agent | Purpose |
|-------|---------|
| `debug-investigator` | Root cause analysis from errors and stack traces |
| `deep-research-got` | Graph of Thoughts framework for complex research |
| `clarity-researcher-writer` | Research first, then write with clarity |
| `production-refactor` | Safe refactoring with dependency analysis |
| `security-vulnerability-hunter` | Scans for injection, XSS, memory issues |

## Hooks

Python hooks via `uv run` handle lifecycle events:

- **pre_tool_use.py** — Safety gate blocking `rm -rf` and `.env` access
- **post_tool_use.py** — Logs all tool results
- **notification.py** — TTS alert when Claude needs input (macOS `say`)
- **session_start.py** — Loads git branch, CONTEXT.md, TODO.md
- **stop.py** — TTS completion message when Claude finishes
- **subagent_stop.py** — TTS notification when subagent completes
- **user_prompt_submit.py** — Logs prompts, generates agent names
- **security_validator.py** — Validates commands for safety
- **capture_events.py** — Event capture for analytics
- **session_summary.py** — Summarizes session on exit
- **stop_learnings.py** — Extracts learnings from completed sessions
- **tab_titles.py** — Dynamic terminal tab titles
- **pre_compact.py** — Pre-compaction hook

## Skills

- **Art** — Excalidraw-style visuals, diagrams, comics
- **Learnings** — Knowledge retention and retrieval
- **Writing** — Literary craft techniques, critique, revise workflows
- **PDF** — Read, merge, split, watermark, encrypt, OCR PDFs
- **Remotion** — Video creation best practices in React

## Rules

Code style enforcement files:

- **comments.md** — No redundant comments, self-documenting code
- **testing.md** — BDD structure (#given, #when, #then)
- **typescript.md** — Naming conventions, type safety

## TTS

Voice notifications use macOS `say` command (no API keys needed). See `hooks/lib/local_tts.py`.

## Setup

Requirements: Python 3.11+, `uv`, Claude Code CLI, macOS (for TTS)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy to Claude config
cp -r . ~/.claude
```

## Customization

Everything is hackable. Hooks are Python scripts. Agents are markdown with system prompts. Skills are self-contained directories.
