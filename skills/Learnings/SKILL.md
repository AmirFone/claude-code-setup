---
name: Learnings
description: Knowledge retention and retrieval system. USE WHEN user asks about past problems, debugging patterns, "have we solved this before", "what did we learn about X", or auto-triggers on debugging keywords. Manages learnings taxonomy and retrieval.
---

# Learnings - Knowledge Retention System

**Auto-routes when user mentions past problems, learnings, or debugging.**

This skill provides a persistent memory system for capturing, organizing, and retrieving learnings from Claude Code sessions.

## Storage Locations

- **Learnings:** `~/.claude/history/learnings/`
- **Taxonomy Index:** `~/.claude/history/learnings/taxonomy.json`
- **Pending Reviews:** `~/.claude/history/learnings/pending/`
- **Sessions:** `~/.claude/history/sessions/`

## Workflow Routing

| Workflow | Trigger | Description |
|----------|---------|-------------|
| **Search** | "check if we've solved this before", "what did we learn about X" | Search past learnings |
| **Review** | "review my learnings", "pending learnings" | Review and confirm pending |
| **Add** | "save this learning", "remember this" | Manually save a learning |
| **Rebalance** | "rebalance taxonomy", "organize learnings" | Reorganize taxonomy tree |

## Natural Language Triggers

The system auto-triggers on these patterns:
- "have we solved this before"
- "check if we've seen this"
- "what did we learn about [X]"
- "any learnings on [X]"
- "recall [X] learning"

## Debugging Auto-Triggers

When these keywords appear in user prompts, the system auto-searches for relevant learnings:
- bug, fix, issue, broken, error, failed
- crash, debug, wrong, unexpected

## Examples

**Example 1: Automatic retrieval during debugging**
```
User: "I'm getting a promise rejection error in my hook"
-> Auto-searches taxonomy for promise/rejection/hook
-> Displays: "Found 2 relevant learnings: [titles]"
```

**Example 2: Explicit search**
```
User: "Have we solved async issues before?"
-> Searches taxonomy: debugging/async/
-> Returns matching learnings with summaries
```

**Example 3: Review pending learnings**
```
User: "review my pending learnings"
-> Lists all pending learnings from recent sessions
-> User confirms or dismisses each
-> Confirmed learnings are filed in taxonomy
```

**Example 4: Save a learning manually**
```
User: "Save this learning about git rebase"
-> Extracts key insight from current context
-> Proposes taxonomy path: tools/git/
-> Creates learning file after confirmation
```

## Taxonomy Structure

Learnings are organized in a hierarchical tree:
```
learnings/
├── debugging/
│   ├── async/
│   └── memory/
├── architecture/
│   └── hooks/
├── tools/
│   ├── git/
│   └── npm/
└── general/
```

The taxonomy grows organically as learnings are added. Claude proposes new branches when needed.

## Learning File Format

Each learning is a markdown file:
```markdown
---
id: learning-2026-01-01-001
title: "Title of the Learning"
created: 2026-01-01T14:22:05Z
source_session: uuid
tags: [debugging/async/promises]
confidence: confirmed
---

# Title

## Problem
What went wrong

## Solution
How to fix it

## Key Insight
The "aha" moment

## Related
- Source session link
```

## Tools

| Tool | Description |
|------|-------------|
| `search_learnings.py` | Natural language taxonomy search |
| `review_pending.py` | Present pending learnings for confirmation |
| `add_learning.py` | Create new learning from context |
| `rebalance.py` | Suggest taxonomy reorganization |

## Integration

- **SessionStart**: Checks for pending learnings to review
- **Stop**: Detects potential learnings, batches for confirmation
- **Auto-trigger**: Debugging keywords trigger search
