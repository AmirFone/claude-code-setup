# CreateSkill Workflow

Create a new skill following the mandatory structure defined in SkillSystem.md.

## Prerequisites

- Read `$PAI_DIR/skills/CORE/SkillSystem.md` for authoritative structure
- Understand TitleCase naming convention

## Steps

### Step 1: Gather Requirements

Ask the user:
1. What should the skill do? (primary purpose)
2. What triggers should invoke it? (USE WHEN keywords)
3. What workflows does it need? (Create, Update, Delete, etc.)
4. Does it need CLI tools? (deterministic operations)

### Step 2: Create Directory Structure

```bash
SKILL_NAME="SkillName"  # TitleCase!
mkdir -p $PAI_DIR/skills/$SKILL_NAME/{Tools,Workflows}
```

### Step 3: Create SKILL.md

Create `$PAI_DIR/skills/$SKILL_NAME/SKILL.md`:

```markdown
---
name: SkillName
description: [What it does]. USE WHEN [intent triggers]. [Additional capabilities].
---

# SkillName

[Brief description of the skill's purpose]

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **Create** | "create [thing]" | `Workflows/Create.md` |
| **List** | "list [things]" | `Workflows/List.md` |

## Examples

**Example 1: [Primary use case]**
\`\`\`
User: "[Example request]"
→ Invokes [Workflow] workflow
→ [Expected result]
\`\`\`

**Example 2: [Secondary use case]**
\`\`\`
User: "[Example request]"
→ [Expected result]
\`\`\`
```

### Step 4: Create Workflow Files

For each workflow in the routing table, create a corresponding file:

```markdown
# WorkflowName Workflow

[Purpose of this workflow]

## Steps

### Step 1: [First action]
[Instructions]

### Step 2: [Second action]
[Instructions]

## Expected Outcome

[What the user should have when complete]
```

### Step 5: Create Tools (if needed)

For deterministic operations, create TypeScript CLI tools:

```typescript
#!/usr/bin/env bun
// $PAI_DIR/skills/SkillName/Tools/ToolName.ts

const args = process.argv.slice(2);
// Implementation
```

### Step 6: Regenerate Index

```bash
bun run $PAI_DIR/Tools/GenerateSkillIndex.ts
```

### Step 7: Register with Claude Code

Create symlink so Claude Code recognizes the skill:

```bash
ln -sf $PAI_DIR/skills/$SKILL_NAME ~/.claude/skills/$SKILL_NAME
```

### Step 8: Verify

```bash
# Check skill appears in index
bun run $PAI_DIR/Tools/SkillSearch.ts --list

# Verify structure
ls -la $PAI_DIR/skills/$SKILL_NAME/
```

## Checklist

- [ ] Skill directory uses TitleCase
- [ ] YAML `name:` uses TitleCase
- [ ] Single-line `description` with `USE WHEN` clause
- [ ] `## Workflow Routing` section with table format
- [ ] `## Examples` section with 2-3 usage patterns
- [ ] `Tools/` directory exists (even if empty)
- [ ] All workflow files use TitleCase
- [ ] Index regenerated
- [ ] Symlink created in `~/.claude/skills/`

## Expected Outcome

A fully functional skill that:
- Routes correctly based on user intent
- Has clear workflow documentation
- Follows TitleCase naming convention
- Appears in skill search results
