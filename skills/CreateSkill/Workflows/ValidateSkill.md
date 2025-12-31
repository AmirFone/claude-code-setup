# ValidateSkill Workflow

Validate an existing skill against the mandatory structure defined in SkillSystem.md.

## Prerequisites

- Read `$PAI_DIR/skills/CORE/SkillSystem.md` for authoritative structure
- Know which skill to validate

## Steps

### Step 1: Identify Skill

Ask user for skill name or path:
```
Which skill would you like to validate?
```

### Step 2: Check Directory Structure

Verify required structure exists:

```bash
SKILL_NAME="SkillName"
SKILL_PATH="$PAI_DIR/skills/$SKILL_NAME"

# Required files/directories
echo "Checking structure..."
test -f "$SKILL_PATH/SKILL.md" && echo "✓ SKILL.md exists" || echo "✗ SKILL.md MISSING"
test -d "$SKILL_PATH/Tools" && echo "✓ Tools/ exists" || echo "✗ Tools/ MISSING"
test -d "$SKILL_PATH/Workflows" && echo "✓ Workflows/ exists" || echo "? Workflows/ (optional)"
```

### Step 3: Validate YAML Frontmatter

Check SKILL.md frontmatter:

**Required:**
- [ ] `name:` field exists and uses TitleCase
- [ ] `description:` field exists
- [ ] Description is single-line (not multi-line `|`)
- [ ] Description contains `USE WHEN` keyword
- [ ] Description is under 1024 characters

**Validation:**
```bash
# Extract frontmatter
head -20 "$SKILL_PATH/SKILL.md" | grep -E "^name:|^description:"
```

### Step 4: Validate Markdown Body

Check for required sections:

- [ ] `## Workflow Routing` section exists
- [ ] Workflow routing uses table format
- [ ] `## Examples` section exists
- [ ] At least 2 examples provided
- [ ] Examples show user input and expected behavior

### Step 5: Validate TitleCase Naming

Check all naming follows TitleCase:

```bash
# Directory name should be TitleCase
echo "$SKILL_NAME" | grep -E "^[A-Z][a-zA-Z]*$" || echo "✗ Directory not TitleCase"

# Workflow files should be TitleCase
ls "$SKILL_PATH/Workflows/"*.md 2>/dev/null | while read f; do
  basename "$f" | grep -E "^[A-Z][a-zA-Z]*.md$" || echo "✗ $f not TitleCase"
done

# Tool files should be TitleCase
ls "$SKILL_PATH/Tools/"*.ts 2>/dev/null | while read f; do
  basename "$f" | grep -E "^[A-Z][a-zA-Z]*.ts$" || echo "✗ $f not TitleCase"
done
```

### Step 6: Validate Workflow References

Ensure all referenced workflows exist:

```bash
# Extract workflow files from routing table
grep -oE "Workflows/[A-Za-z]+\.md" "$SKILL_PATH/SKILL.md" | while read wf; do
  test -f "$SKILL_PATH/$wf" && echo "✓ $wf exists" || echo "✗ $wf MISSING"
done
```

### Step 7: Generate Validation Report

Produce summary:

```markdown
## Validation Report: [SkillName]

### Structure
- SKILL.md: [PASS/FAIL]
- Tools/: [PASS/FAIL]
- Workflows/: [PASS/OPTIONAL]

### Frontmatter
- name field: [PASS/FAIL]
- description field: [PASS/FAIL]
- USE WHEN keyword: [PASS/FAIL]
- TitleCase naming: [PASS/FAIL]

### Body
- Workflow Routing: [PASS/FAIL]
- Examples section: [PASS/FAIL]

### Files
- Referenced workflows exist: [PASS/FAIL]
- TitleCase filenames: [PASS/FAIL]

**Overall: [VALID/NEEDS FIXES]**
```

## Expected Outcome

A clear validation report showing:
- What passes the skill structure requirements
- What needs to be fixed
- Specific recommendations for fixes

## Next Steps

If validation fails, recommend:
- Use `CanonicalizeSkill` workflow to auto-fix issues
- Manual fixes for content problems
