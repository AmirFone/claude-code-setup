# Rebalance Workflow

## When to Use
- Taxonomy depth exceeds 5 levels
- A branch has more than 10 siblings
- A branch has fewer than 2 learnings
- User requests "rebalance my learnings"
- Periodic maintenance

## Trigger Thresholds
- **Flatten**: Depth > 5 levels
- **Group**: Branch > 10 siblings
- **Merge**: Branch < 2 learnings

## Steps

1. **Analyze Taxonomy**
   ```bash
   uv run ~/.claude/skills/Learnings/Tools/rebalance.py --analyze
   ```

2. **Review Suggestions**
   Each suggestion includes:
   - Type (flatten/group/merge)
   - Path in taxonomy
   - Reason for suggestion
   - Recommended action

3. **Apply Changes**
   ```bash
   # Apply specific suggestion
   uv run ~/.claude/skills/Learnings/Tools/rebalance.py --apply 1
   ```

4. **View History**
   ```bash
   uv run ~/.claude/skills/Learnings/Tools/rebalance.py --history
   ```

## Suggestion Types

### Flatten
- Triggered when nesting is too deep
- Moves all sub-learnings up to reduce depth
- Preserves all learning content

### Group
- Triggered when too many siblings at one level
- Requires manual intervention
- Suggest grouping related branches

### Merge
- Triggered when branch has very few learnings
- Requires manual intervention
- Suggest merging with sibling or parent

## Example

```
$ rebalance.py --analyze

Found 2 suggestion(s):

[1] FLATTEN
    Path: debugging/async/promises/rejection/unhandled
    Reason: Depth (6) exceeds maximum (5)
    Action: Consider flattening branches under 'debugging/async/promises/rejection/unhandled'

[2] MERGE
    Path: tools/git
    Reason: Sparse branch with only 1 learning(s)
    Action: Consider merging 'tools/git' with a sibling or parent

To apply a suggestion: rebalance.py --apply <number>
```
