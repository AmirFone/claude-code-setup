# CanonicalizeSkill Workflow

Fix an existing skill to comply with the mandatory structure defined in SkillSystem.md.

## Prerequisites

- Read `$PAI_DIR/skills/CORE/SkillSystem.md` for authoritative structure
- Run `ValidateSkill` workflow first to identify issues
- Know which skill to fix

## Steps

### Step 1: Identify Issues

Run validation first:
```
Invoke ValidateSkill workflow on [skill name]
```

Common issues:
- Non-TitleCase directory name
- Non-TitleCase file names
- Missing `USE WHEN` in description
- Multi-line description
- Missing Examples section
- Missing Workflow Routing table
- Missing Tools/ directory

### Step 2: Fix Directory Name

If directory is not TitleCase:

```bash
OLD_NAME="old-skill-name"
NEW_NAME="OldSkillName"  # Convert to TitleCase

mv "$PAI_DIR/skills/$OLD_NAME" "$PAI_DIR/skills/$NEW_NAME"
```

### Step 3: Fix YAML Frontmatter

If description is multi-line, convert to single-line:

**Before:**
```yaml
---
name: skill-name
description: |
  This skill does things.
  It has multiple lines.
---
```

**After:**
```yaml
---
name: SkillName
description: This skill does things. USE WHEN user wants to do things. Has multiple capabilities.
---
```

**Rules:**
- `name` must be TitleCase
- `description` must be single line
- Must contain `USE WHEN`
- Max 1024 characters

### Step 4: Fix File Names

Rename files to TitleCase:

```bash
SKILL_PATH="$PAI_DIR/skills/SkillName"

# Rename workflow files
for f in "$SKILL_PATH/Workflows/"*.md; do
  base=$(basename "$f" .md)
  # Convert kebab-case or snake_case to TitleCase
  new_base=$(echo "$base" | sed -r 's/(^|[-_])([a-z])/\U\2/g')
  mv "$f" "$SKILL_PATH/Workflows/$new_base.md"
done

# Rename tool files
for f in "$SKILL_PATH/Tools/"*.ts; do
  base=$(basename "$f" .ts)
  new_base=$(echo "$base" | sed -r 's/(^|[-_])([a-z])/\U\2/g')
  mv "$f" "$SKILL_PATH/Tools/$new_base.ts"
done
```

### Step 5: Add Missing Sections

If `## Workflow Routing` missing, add:

```markdown
## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **[Action]** | "[trigger phrase]" | `Workflows/[Action].md` |
```

If `## Examples` missing, add:

```markdown
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

### Step 6: Create Missing Directories

```bash
SKILL_PATH="$PAI_DIR/skills/SkillName"

# Ensure Tools/ exists
mkdir -p "$SKILL_PATH/Tools"

# Ensure Workflows/ exists if referenced
mkdir -p "$SKILL_PATH/Workflows"
```

### Step 7: Update Internal References

If file names changed, update references in SKILL.md:

```bash
# Update workflow routing table
sed -i 's/old-workflow\.md/OldWorkflow.md/g' "$SKILL_PATH/SKILL.md"
```

### Step 8: Regenerate Index

```bash
bun run $PAI_DIR/Tools/GenerateSkillIndex.ts
```

### Step 9: Verify Fix

Run validation again:
```
Invoke ValidateSkill workflow on [skill name]
```

All checks should now pass.

## Checklist

- [ ] Directory name is TitleCase
- [ ] YAML `name:` is TitleCase
- [ ] Description is single-line with `USE WHEN`
- [ ] All workflow files are TitleCase
- [ ] All tool files are TitleCase
- [ ] `## Workflow Routing` section exists
- [ ] `## Examples` section exists
- [ ] `Tools/` directory exists
- [ ] Internal references updated
- [ ] Index regenerated

## Expected Outcome

A skill that:
- Passes all validation checks
- Follows TitleCase naming convention
- Has complete required sections
- Routes correctly in the skill system
