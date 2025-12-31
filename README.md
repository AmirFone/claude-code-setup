# My Claude Code Setup

Hey, I'm Amir. I spend most of my day working with Claude Code, and over time I've built up a set of hooks, agents, and utilities that make the experience way better. This repo is everything I use.

## Why I Built This

Claude Code is powerful out of the box. But I wanted more control. I wanted to know when tasks finished without staring at my terminal. I wanted safety rails so Claude couldn't accidentally nuke my home directory. I wanted specialized agents for different types of work.

So I built this.

## What's Inside

**8 hooks** that run at different points in Claude's workflow. They handle safety checks, logging, and audio notifications.

**5 agents** that specialize in debugging, research, writing, refactoring, and security analysis.

**3 TTS providers** that talk to you when Claude finishes work. Yes, actual audio. It's surprisingly useful.

**3 LLM backends** that generate completion messages and agent names on the fly.

## The Hooks

Every hook runs via `uv run` and gets configured in `settings.json`. Here's what each one does:

### `pre_tool_use.py` - The Safety Gate

This one runs before Claude executes any tool. It blocks dangerous stuff:
- Any `rm -rf` variant that could wipe directories
- Access to `.env` files (your secrets stay secret)

Everything else gets logged to `logs/pre_tool_use.json`. I can go back and see exactly what Claude did in any session.

### `post_tool_use.py` - Logging What Happened

Records the results of every tool call. Good for debugging when something goes wrong.

### `notification.py` - "Your Agent Needs Input"

When Claude stops and waits for you, this hook speaks up. Literally. It uses TTS to say "Your agent needs your input" so you can step away from the screen and still know when to come back.

### `session_start.py` - Context Loading

When you start a session, this hook:
- Checks your git branch and uncommitted changes
- Loads `CONTEXT.md` and `TODO.md` if they exist
- Pulls recent GitHub issues if `gh` CLI is installed

Claude starts each session knowing what you're working on.

### `stop.py` - The Finish Line

When Claude finishes, this hook:
1. Asks an LLM to generate a friendly completion message
2. Speaks it out loud via TTS
3. Logs everything to `logs/stop.json`

Instead of just stopping, Claude says something like "All done, ready for your next task!" It sounds small but it changes the feel completely.

### `user_prompt_submit.py` - Prompt Logging and Agent Naming

Logs every prompt you send. Also generates unique agent names using an LLM. Names like "Phoenix" or "Catalyst" instead of "Agent-1234."

### `pre_compact.py` and `subagent_stop.py`

Handle context compaction and subagent completion. Less exciting but necessary for keeping things running smoothly.

## The Agents

These live in the `agents/` directory. Each has a frontmatter block with name, description, model, and color.

### `debug-investigator`

For tracking down bugs. Give it an error message or stack trace and it traces the issue back to the exact line of code. Uses root cause analysis instead of just finding symptoms.

### `deep-research-got`

My most complex agent. It implements a Graph of Thoughts framework for serious research. Creates a folder structure with research contracts, evidence ledgers, contradiction logs, and a full audit trail. Overkill for simple questions. Perfect for decisions that matter.

### `clarity-researcher-writer`

Research first, write second. It gathers context from your codebase and session, then writes with strict clarity rules. No filler words, no marketing speak, just direct communication.

### `production-refactor`

For cleaning up code. Handles the boring work of renaming, restructuring, and modernizing without breaking anything.

### `security-vulnerability-hunter`

Scans your codebase for security issues. Prompt injection, XSS, SQL injection, null pointer bugs, memory issues. Reports exact file paths and line numbers with proof-of-concept payloads.

## TTS - The Fun Part

I wanted to know when Claude finished without watching the terminal. So I added voice notifications.

The system picks the best available provider:

1. **ElevenLabs** (needs `ELEVENLABS_API_KEY`) - Best quality. Uses Turbo v2.5 model.
2. **OpenAI** (needs `OPENAI_API_KEY`) - Good quality with streaming.
3. **pyttsx3** - No API needed. Works offline. Sounds robotic but gets the job done.

Set your API keys in `.env` and the hooks automatically use the best available option.

## LLM Backends

Completion messages and agent names come from LLMs. Same fallback pattern:

1. **OpenAI** - GPT-4o-mini for fast responses
2. **Anthropic** - Claude 3.5 Haiku
3. **Ollama** - Local models, no API needed
4. **Hardcoded** - Fallback phrases if nothing else works

## Logging

Every hook writes to `logs/` in your project directory. JSON files you can grep through later. Useful for:
- Debugging hook issues
- Auditing what Claude did
- Building analytics on your usage

## Setup

You'll need:
- Python 3.11 or higher
- `uv` package manager
- Claude Code CLI

Install uv if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Copy this repo to your Claude config location:

```bash
cp -r . ~/.claude
```

Add your API keys (optional but recommended):

```bash
cp .env.sample .env
# Edit .env with your keys
```

Available environment variables:
- `ELEVENLABS_API_KEY` - For high-quality TTS
- `OPENAI_API_KEY` - For TTS and completion messages
- `ANTHROPIC_API_KEY` - For completion messages
- `ENGINEER_NAME` - Your name (used in personalized messages)

## Make It Yours

This setup works for how I work. Fork it and change whatever doesn't fit your workflow. The hooks are just Python scripts. The agents are just markdown files with system prompts. Everything is readable and hackable.

If you build something cool on top of this, I'd love to hear about it.
