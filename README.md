# Claude Code Setup

Custom hooks, agents, skills, and rules for Claude Code.

## Structure

```
├── agents/          # 5 specialized agents
├── hooks/           # Python lifecycle hooks + TTS/LLM utils
├── skills/          # Art, Learnings, Writing
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
- **notification.py** — TTS alert when Claude needs input
- **session_start.py** — Loads git branch, CONTEXT.md, TODO.md
- **stop.py** — TTS completion message when Claude finishes
- **user_prompt_submit.py** — Logs prompts, generates agent names

## Skills

- **Art** — Excalidraw-style visuals, diagrams, comics
- **Learnings** — Knowledge retention and retrieval
- **Writing** — Literary craft techniques, critique, revise workflows

## Rules

Code style enforcement files:

- **comments.md** — No redundant comments, self-documenting code
- **testing.md** — BDD structure (#given, #when, #then)
- **typescript.md** — Naming conventions, type safety

## TTS Providers

Voice notifications when Claude finishes (auto-selects best available):

1. **ElevenLabs** — Best quality (needs `ELEVENLABS_API_KEY`)
2. **OpenAI** — Good quality (needs `OPENAI_API_KEY`)
3. **pyttsx3** — Offline fallback

## LLM Backends

For completion messages and agent names:

1. OpenAI (GPT-4o-mini)
2. Anthropic (Claude 3.5 Haiku)
3. Ollama (local)
4. Hardcoded fallback

## Setup

Requirements: Python 3.11+, `uv`, Claude Code CLI

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy to Claude config
cp -r . ~/.claude

# Add API keys (optional)
cp .env.sample .env
```

Environment variables:
- `ELEVENLABS_API_KEY` — TTS
- `OPENAI_API_KEY` — TTS + completion messages
- `ANTHROPIC_API_KEY` — Completion messages

## Customization

Everything is hackable. Hooks are Python scripts. Agents are markdown with system prompts. Skills are self-contained directories.
