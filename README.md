# My Claude Code Setup

I spend most of my day working with Claude Code. This repo is everything I've built to make that experience better.

## The Problem

Claude Code ships powerful. But I kept wanting things it didn't do:

- I'd walk away from my terminal, miss the moment Claude finished, come back twenty minutes later
- Claude would run `rm -rf` on something important
- I had no record of what happened in a session when things went wrong
- Every task got the same generalist treatment, whether debugging or research or refactoring

So I built fixes for all of it.

## What's Here

**Two hook systems** — Python hooks for core functionality, TypeScript hooks for extended capabilities.

**5 specialized agents** for debugging, research, writing, refactoring, and security scanning.

**6 skills** that extend Claude's capabilities. Writing craft, agent composition, visual generation, meta-prompting.

**3 TTS providers** that announce when Claude finishes. Your computer talks to you. It sounds gimmicky until you try it.

**3 LLM backends** for generating completion messages and agent names on the fly.

## The Hooks

Two hook systems run in parallel. Python hooks via `uv run` handle core functionality. TypeScript hooks via `bun run` handle extended features. Configuration lives in `settings.json`.

### Python Hooks (Core)

#### `pre_tool_use.py`

The safety gate. Runs before Claude executes any tool.

It blocks:
- `rm -rf` variants that could wipe directories
- Access to `.env` files

Everything else gets logged to `logs/pre_tool_use.json`. Every tool call, timestamped. Useful when you need to reconstruct what Claude did.

#### `post_tool_use.py`

Records results of every tool call. When something breaks, you'll know exactly what happened.

#### `notification.py`

When Claude stops and waits for input, this hook speaks: "Your agent needs your input." Out loud. Through your speakers.

You can leave the room. You'll know when to come back.

#### `session_start.py`

Runs when you start a session. Checks your git branch, loads `CONTEXT.md` and `TODO.md` if they exist, pulls recent GitHub issues if `gh` CLI is installed.

Claude starts each session knowing what you're working on.

#### `stop.py`

When Claude finishes:
1. An LLM generates a completion message
2. TTS speaks it aloud
3. Everything logs to `logs/stop.json`

Instead of silence, Claude says "All done, ready for your next task." Small change. Different feel.

#### `user_prompt_submit.py`

Logs every prompt you send. Also generates unique agent names through an LLM—names like "Phoenix" or "Catalyst" instead of "Agent-1234."

#### `pre_compact.py` and `subagent_stop.py`

Handle context compaction and subagent completion. Plumbing. Necessary plumbing.

### TypeScript Hooks (Extended)

These run via `bun` from `~/.config/pai/hooks/`. They add:

- **security-validator.ts** — Extra validation layer for Bash commands
- **capture-all-events.ts** — Comprehensive event logging across all hook types
- **stop-hook-history.ts** — Saves session history on stop
- **stop-hook-voice.ts** — Additional voice notifications
- **subagent-stop-hook.ts** — Subagent completion handling
- **subagent-stop-hook-voice.ts** — Voice notifications for subagents
- **update-tab-titles.ts** — Dynamic terminal tab naming
- **initialize-session.ts** — Session initialization
- **load-core-context.ts** — Loads CORE skill context at session start
- **capture-session-summary.ts** — Captures summary when session ends

## The Agents

Each lives in `agents/` with frontmatter defining name, description, model, and color.

### `debug-investigator`

Give it an error message or stack trace. It traces the issue to the exact line of code. Root cause analysis, not symptom hunting.

### `deep-research-got`

My most complex agent. Implements a Graph of Thoughts framework. Creates a folder structure with research contracts, evidence ledgers, contradiction logs, full audit trail.

Overkill for simple questions. Perfect for decisions that matter.

### `clarity-researcher-writer`

Research first, write second. Gathers context from your codebase and session, then writes with strict clarity rules. No filler. No marketing speak. Direct communication.

### `production-refactor`

Transforms prototype code into production-grade systems. Performs dependency analysis before touching anything. Maps all imports, traces data flow, assesses risk levels. Makes incremental changes with verification at each step.

Never changes public interfaces without approval. Never deletes functionality without confirming it's unused.

### `security-vulnerability-hunter`

Scans for prompt injection, XSS, SQL injection, null pointer bugs, memory issues. Reports exact file paths and line numbers with proof-of-concept payloads.

## The Skills

Skills live in `skills/`. Each is a self-contained capability with its own workflows, templates, and tools.

### `CORE`

Auto-loads at session start. Defines identity, personality calibration, response format, and contact information. The foundation everything else builds on.

### `Writing`

Literary craftsman mode. Synthesizes techniques from Hemingway, McCarthy, Highsmith, Ishiguro, Morrison, Orwell, and Didion. Three workflows: write, critique, revise.

Has a banned words list. If I catch myself writing "delve" or "leverage," this skill intervenes.

### `Agents`

Dynamic agent composition. Spin up custom agents with specific personality traits, expertise areas, and voice mappings. Routes between named agents (persistent identities) and dynamic agents (task-specific specialists).

### `Prompting`

Meta-prompting system. Templates, standards, and tools for programmatic prompt generation. Handlebars-based rendering with validation.

### `Art`

Visual content generation with Excalidraw hand-drawn aesthetic. Technical diagrams, blog headers, comics. Dark mode backgrounds, bright accents.

### `CreateSkill`

The skill that creates skills. Enforces structure, validates format, handles canonicalization.

## Additional Features

### Status Line

Custom status line showing model, current directory, and context window usage percentage. Configured in `settings.json`.

### Plugins

Two plugins enabled:
- **frontend-design** — For building frontend interfaces
- **ralph-wiggum** — Loop detection and prevention

### Always Thinking

`alwaysThinkingEnabled: true` — Claude shows its reasoning process.

## TTS

I wanted to know when Claude finished without staring at my terminal. Voice notifications solved this.

The system picks the best available provider:

1. **ElevenLabs** (needs `ELEVENLABS_API_KEY`) — Best quality. Turbo v2.5 model.
2. **OpenAI** (needs `OPENAI_API_KEY`) — Good quality. Streams.
3. **pyttsx3** — No API. Works offline. Sounds robotic. Gets the job done.

Set your API keys in `.env`. The hooks use the best available option automatically.

## LLM Backends

Completion messages and agent names come from LLMs. Same fallback pattern:

1. **OpenAI** — GPT-4o-mini. Fast.
2. **Anthropic** — Claude 3.5 Haiku.
3. **Ollama** — Local models. No API needed.
4. **Hardcoded** — Fallback phrases when nothing else works.

## Logging

Every hook writes JSON to `logs/` in your project directory. Useful for:
- Debugging hook issues
- Auditing what Claude did
- Building usage analytics

## Setup

You need:
- Python 3.11+
- `uv` package manager
- `bun` runtime (for TypeScript hooks)
- Claude Code CLI

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install bun:

```bash
curl -fsSL https://bun.sh/install | bash
```

Copy this repo to your Claude config:

```bash
cp -r . ~/.claude
```

Add your API keys (optional but recommended):

```bash
cp .env.sample .env
# Edit .env with your keys
```

Environment variables:
- `ELEVENLABS_API_KEY` — High-quality TTS
- `OPENAI_API_KEY` — TTS and completion messages
- `ANTHROPIC_API_KEY` — Completion messages
- `ENGINEER_NAME` — Your name (for personalized messages)

## Make It Yours

This setup works for how I work. Fork it. Change whatever doesn't fit.

The hooks are Python and TypeScript scripts. The agents are markdown files with system prompts. The skills are self-contained directories. Everything is readable. Everything is hackable.

If you build something interesting on top of this, I'd like to hear about it.
