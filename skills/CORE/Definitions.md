# Canonical Definitions

## Core Concepts

### PAI (Personal AI Infrastructure)
A modular, extensible system for managing AI agent capabilities, history, and workflows. Built on principles of determinism, composability, and continuous learning.

### Skill
A self-contained capability module with:
- `SKILL.md` - Main entry point with routing and documentation
- `Tools/` - CLI executables (deterministic code)
- `Workflows/` - Step-by-step procedures
- `Data/` - Configuration and reference data

### Pack
An installable unit that adds functionality to PAI. Packs can contain skills, hooks, tools, or infrastructure components.

### Bundle
A curated collection of packs designed to work together. Bundles provide a complete capability set (e.g., the Kai Bundle).

### Hook
An event-driven automation that triggers on Claude Code events (PreToolUse, PostToolUse, Stop, etc.). Hooks enable observability, security, and automation.

---

## Agent Terminology

### Main Agent
The primary Claude Code session running in the user's terminal. Has full capabilities and spawns subagents as needed.

### Subagent (Intern)
A specialized agent spawned by Task tool for specific subtasks. Has limited context but focused capabilities.

### Trait
A behavioral characteristic that modifies agent behavior (e.g., "thorough", "skeptical", "creative"). Traits compose to create agent personalities.

### Personality
A combination of traits that define how an agent approaches tasks. Personalities map to voice and interaction style.

---

## System Components

### History System
Captures and organizes:
- **Sessions** - Complete interaction records
- **Learnings** - Insights and discoveries
- **Research** - Investigation results
- **Decisions** - Key choices and rationale

### Hook System
Event-driven automation layer providing:
- Security validation
- Event capture
- Voice notifications
- Context loading

### Observability System
Real-time monitoring dashboard showing:
- Tool calls
- Agent activity
- Event timeline
- Session state

### Voice System
Text-to-speech notification layer with:
- ElevenLabs integration
- Personality-specific voices
- Prosody enhancement

---

## File Types

### SKILL.md
Main entry point for a skill. Contains:
- YAML frontmatter with metadata
- Description with USE WHEN clause
- Workflow routing table
- Examples

### Workflow (*.md)
Step-by-step procedure document with:
- Clear action steps
- Decision points
- Expected outcomes

### Tool (*.ts)
CLI executable that:
- Takes arguments
- Performs deterministic operations
- Returns structured output

### Template (*.hbs)
Handlebars template for:
- Prompt generation
- Document formatting
- Structured output

---

## Events

| Event | When | Use |
|-------|------|-----|
| `SessionStart` | New Claude Code session begins | Load context, initialize |
| `SessionEnd` | Session terminates | Capture summary |
| `PreToolUse` | Before tool executes | Security validation |
| `PostToolUse` | After tool completes | Capture results |
| `UserPromptSubmit` | User sends message | Update context |
| `Stop` | Main agent completes | Voice notification |
| `SubagentStop` | Subagent completes | Capture research |

---

## Paths

| Variable | Default | Purpose |
|----------|---------|---------|
| `PAI_DIR` | `~/.config/pai` | Root PAI directory |
| `$PAI_DIR/skills/` | - | Skill modules |
| `$PAI_DIR/hooks/` | - | Event handlers |
| `$PAI_DIR/history/` | - | Captured records |
| `$PAI_DIR/Tools/` | - | Global CLI tools |

---

## Acronyms

- **PAI** - Personal AI Infrastructure
- **CLI** - Command Line Interface
- **TTS** - Text-to-Speech
- **RLS** - Row-Level Security
- **LLM** - Large Language Model
- **JSONL** - JSON Lines (newline-delimited JSON)
