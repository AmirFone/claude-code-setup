# Claude Code Power User Configuration

A production-grade Claude Code setup with safety hooks, TTS notifications, comprehensive logging, and specialized sub-agents for research, debugging, and security analysis.

## What This Does

This configuration turns Claude Code into a supervised, auditable coding assistant. Every tool call gets logged. Dangerous commands get blocked. You get audio notifications when the agent needs input or finishes work. Specialized agents handle deep research, bug investigation, and security scanning.

## Quick Start

```bash
# Clone to your home directory
git clone https://github.com/yourusername/claude-code-config ~/.claude

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up environment variables (optional, for TTS)
cp ~/.claude/.env.sample ~/.claude/.env
# Edit .env with your API keys
```

## File Structure

```
~/.claude/
├── settings.json              # Main Claude Code configuration
├── agents/                    # Custom sub-agents
│   ├── deep-research-got.md      # Graph of Thoughts research
│   ├── clarity-researcher-writer.md  # Research-first writing
│   ├── debug-investigator.md     # Bug root cause analysis
│   └── security-vulnerability-hunter.md  # Security scanning
├── hooks/                     # Event hook scripts
│   ├── pre_tool_use.py           # Safety checks before tools run
│   ├── post_tool_use.py          # Logging after tools run
│   ├── notification.py           # TTS when agent needs input
│   ├── stop.py                   # TTS and logging on completion
│   ├── subagent_stop.py          # Subagent completion handling
│   ├── user_prompt_submit.py     # Prompt logging and agent naming
│   ├── pre_compact.py            # Context compaction logging
│   ├── session_start.py          # Session initialization
│   └── utils/
│       ├── tts/
│       │   ├── elevenlabs_tts.py    # ElevenLabs TTS (best quality)
│       │   ├── openai_tts.py        # OpenAI TTS (second choice)
│       │   └── pyttsx3_tts.py       # Local TTS (fallback)
│       └── llm/
│           ├── oai.py               # OpenAI for completion messages
│           ├── anth.py              # Anthropic fallback
│           └── ollama.py            # Local Ollama fallback
└── plugins/                   # Installed plugins
    └── ...
```

## Configuration Details

### settings.json

The main configuration file enables:

**Hooks for all major events:**
- `PreToolUse` - Runs safety checks before any tool executes
- `PostToolUse` - Logs tool results
- `Notification` - Announces when agent needs input
- `Stop` - Announces completion, saves chat transcript
- `SubagentStop` - Handles subagent completion
- `UserPromptSubmit` - Logs prompts, generates agent names
- `PreCompact` - Runs before context compaction
- `SessionStart` - Initializes new sessions

**Custom status line** showing:
- Current model name
- Working directory
- Context window usage percentage

**Always-thinking mode** enabled for extended reasoning.

**Frontend-design plugin** enabled for UI generation.

### Hook Scripts

#### pre_tool_use.py - Safety Gate

Blocks dangerous operations before they execute:

**Blocked commands:**
- `rm -rf` and all variations (`rm -fr`, `rm --recursive --force`)
- Recursive deletion targeting `/`, `~`, `$HOME`, `..`, or wildcards
- Any access to `.env` files (protects secrets)

**Allowed:**
- `.env.sample` files (templates are fine)
- Non-recursive rm commands
- All other operations (logged but not blocked)

Exit codes:
- `0` - Allow the tool to run
- `2` - Block the tool and show error to Claude

#### post_tool_use.py - Result Logging

Logs all tool execution results to `logs/post_tool_use.json`. Useful for debugging and auditing what Claude did during a session.

#### notification.py - Input Needed Alert

When Claude needs your input:
1. Selects best available TTS (ElevenLabs > OpenAI > pyttsx3)
2. Announces "Your agent needs your input"
3. 30% chance to include your name (set `ENGINEER_NAME` env var)

Skips generic "Claude is waiting for your input" messages to reduce noise.

#### stop.py - Completion Handler

When Claude finishes work:
1. Logs stop event to `logs/stop.json`
2. Saves full chat transcript to `logs/chat.json` (with `--chat` flag)
3. Generates completion message via LLM (OpenAI > Anthropic > Ollama > fallback)
4. Announces completion via TTS (with `--notify` flag)

#### subagent_stop.py - Subagent Completion

Handles completion of Task tool subagents. Announces "Subagent Complete" via TTS and logs to `logs/subagent_stop.json`.

#### user_prompt_submit.py - Prompt Handling

Features:
- Logs all prompts to `logs/user_prompt_submit.json`
- Stores session data in `.claude/data/sessions/{session_id}.json`
- Generates unique agent names (with `--name-agent` flag)
- Optional prompt validation (with `--validate` flag)

#### pre_compact.py - Compaction Prep

Runs before context window compaction:
- Logs compaction events (manual vs auto-triggered)
- Optional transcript backup (with `--backup` flag)
- Backups saved to `logs/transcript_backups/`

#### session_start.py - Session Init

Initializes new sessions with optional context loading:
- Git branch and uncommitted changes count
- Content from `.claude/CONTEXT.md`, `TODO.md`
- Recent GitHub issues (if `gh` CLI available)
- Optional TTS announcement (with `--announce` flag)

## Custom Agents

### deep-research-got.md

A Graph of Thoughts research agent for decision-grade investigation.

**Question complexity classification:**
- Type A (Lookup) - Single fact, skip GoT, 1-2 minutes
- Type B (Synthesis) - Multiple facts, abbreviated GoT, 15 minutes
- Type C (Analysis) - Multiple perspectives, full 7-phase GoT, 30-60 minutes
- Type D (Investigation) - Novel question, extended GoT + Red Team, 2-4 hours

**Research phases:**
1. Question scoping and contract
2. Hypothesis formation (3-5 testable hypotheses)
3. Retrieval planning with subquestions
4. Iterative querying with GoT loop
5. Source triangulation and contradiction resolution
6. Knowledge synthesis with implications analysis
7. Quality assurance with claim verification

**Output structure:**
```
/RESEARCH/[project_name]/
├── README.md
├── 00_research_contract.md
├── 01_research_plan.md
├── 02_query_log.csv
├── 03_source_catalog.csv
├── 04_evidence_ledger.csv
├── 05_contradictions_log.md
├── 08_report/
│   ├── 00_executive_summary.md
│   ├── 06_options_recommendations.md
│   └── ...
└── 09_qa/
    └── qa_report.md
```

### clarity-researcher-writer.md

Research-first writing agent that:
1. Gathers context from session and files (silently)
2. Writes with maximum clarity

**Writing rules:**
- Lead with the answer
- Use plain language (10-year-old test)
- Keep sentences under 15 words
- Cut ruthlessly (no filler, no hedging)
- Active voice, direct address
- No banned phrases ("leverage", "robust", "dive into", etc.)

### debug-investigator.md

Bug investigation agent with systematic methodology:

**Phase 1: Evidence Collection**
- Parse error messages, stack traces, reproduction steps
- Extract file names, line numbers, function names

**Phase 2: Codebase Investigation**
- Trace execution paths
- Search for error strings and related patterns
- Examine dependencies and configs

**Phase 3: Hypothesis Formation**
- Generate multiple possible causes
- Validate against code evidence
- Eliminate impossibilities

**Phase 4: Root Cause Identification**
- Pinpoint exact location (file, function, line)
- Explain the mechanism
- Trace the cause-and-effect chain

**Output format includes:**
- Investigation summary
- Root cause location with code snippets
- Evidence chain
- Recommended fix
- Related concerns

### security-vulnerability-hunter.md

Comprehensive security scanner covering:

**Vulnerability categories:**
- Prompt injection (direct and indirect)
- Client-side (XSS, CSRF, DOM-based attacks)
- Application-level (SQLi, SSRF, IDOR, auth bypass)
- Code-level (null pointers, buffer overflows, memory issues)

**Analysis methodology:**
1. Reconnaissance - Map entry points and inputs
2. Deep trace analysis - Follow every code path
3. Vulnerability confirmation - Trace complete attack paths
4. Root cause analysis - Find systemic issues

**Output per vulnerability:**
- Severity rating (Critical/High/Medium/Low)
- Exact location (file, line, function)
- Root cause explanation
- Attack vector description
- Code path trace
- Impact assessment
- Proof of concept
- Remediation steps

## Environment Variables

Create `~/.claude/.env` with:

```bash
# TTS Configuration (optional, in priority order)
ELEVENLABS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# LLM for completion messages (optional)
ANTHROPIC_API_KEY=your_key_here

# Personalization
ENGINEER_NAME=YourName
```

TTS priority: ElevenLabs (best quality) > OpenAI > pyttsx3 (local, no API needed)

LLM priority for completion messages: OpenAI > Anthropic > Ollama > hardcoded fallback

## Logs Directory

Each project creates a `logs/` directory with:

```
logs/
├── pre_tool_use.json      # All tool calls before execution
├── post_tool_use.json     # All tool results
├── notification.json      # Input-needed events
├── stop.json              # Session stop events
├── subagent_stop.json     # Subagent completions
├── user_prompt_submit.json # All user prompts
├── pre_compact.json       # Context compaction events
├── session_start.json     # Session start events
├── chat.json              # Full chat transcript (if --chat enabled)
└── transcript_backups/    # Pre-compaction backups (if --backup enabled)
```

## Customization

### Add New Safety Rules

Edit `~/.claude/hooks/pre_tool_use.py`:

```python
# Add to is_dangerous_rm_command() patterns list
patterns = [
    r'\brm\s+.*-[a-z]*r[a-z]*f',
    # Add your pattern here
]

# Or add new file access rules to is_env_file_access()
if '.secrets' in file_path:
    return True
```

### Disable TTS

Remove `--notify` from hook commands in `settings.json`:

```json
"Stop": [{
    "hooks": [{
        "command": "uv run ~/.claude/hooks/stop.py --chat"
    }]
}]
```

### Add Custom Agents

Create a new file in `~/.claude/agents/`:

```markdown
---
name: my-agent
description: When to use this agent with examples
model: opus
color: blue
---

Your agent instructions here.
```

### Change TTS Voice

Edit the TTS utility scripts in `~/.claude/hooks/utils/tts/`:

- ElevenLabs: Change `voice_id` in `elevenlabs_tts.py`
- OpenAI: Change `voice` parameter in `openai_tts.py`

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Claude Code CLI

Optional:
- ElevenLabs API key (best TTS quality)
- OpenAI API key (TTS and completion messages)
- Anthropic API key (completion messages fallback)
- Ollama (local LLM fallback)
- GitHub CLI (`gh`) for session context

## Troubleshooting

**Hooks not running:**
- Check that `uv` is installed and in PATH
- Verify hook scripts are executable: `chmod +x ~/.claude/hooks/*.py`
- Check `settings.json` syntax

**TTS not working:**
- Verify API keys in `.env`
- Test directly: `uv run ~/.claude/hooks/utils/tts/pyttsx3_tts.py "test"`
- Check audio output device

**Safety hook blocking too much:**
- Review `pre_tool_use.py` patterns
- Check logs in `logs/pre_tool_use.json` for what's being blocked

**Agents not triggering:**
- Agent files must be in `~/.claude/agents/`
- Check frontmatter syntax (name, description, model required)
- Description must include clear trigger examples

## License

MIT
