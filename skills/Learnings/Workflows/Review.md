# Review Workflow

## When to Use
- User says "review my pending learnings"
- Session start shows pending learnings notification
- User wants to confirm or dismiss detected learnings

## Steps

1. **Check Pending**
   ```bash
   uv run ~/.claude/skills/Learnings/Tools/review_pending.py
   ```

2. **Present Each Learning**
   For each pending learning, show:
   - Title
   - Problem detected
   - Solution detected
   - Proposed taxonomy location
   - Confidence score

3. **User Decision**
   - Confirm: Learning is filed in taxonomy
   - Dismiss: Learning is discarded
   - Edit: Modify before confirming

4. **Execute Decision**
   ```bash
   # Confirm specific learning
   uv run ~/.claude/skills/Learnings/Tools/review_pending.py --confirm 1

   # Dismiss specific learning
   uv run ~/.claude/skills/Learnings/Tools/review_pending.py --dismiss 2

   # Confirm all
   uv run ~/.claude/skills/Learnings/Tools/review_pending.py --confirm-all
   ```

5. **Update Taxonomy**
   - Confirmed learnings are written to taxonomy tree
   - taxonomy.json is updated with new entries

## Example

User: "review my pending learnings"

Output:
```
Pending Learnings (3):

[1] Hook Exit Code Handling (confidence: 0.85)
    Problem: Hook was returning exit code 1 instead of 0
    Solution: Changed sys.exit(1) to sys.exit(0) for success
    Proposed: debugging/hooks/exit-codes

[2] JSON Parsing in Hooks (confidence: 0.72)
    ...

Commands: --confirm N, --dismiss N, --confirm-all
```
