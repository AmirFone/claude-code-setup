# Search Workflow

## When to Use
- User asks "have we solved this before?"
- User asks "what did we learn about X?"
- User mentions debugging keywords (bug, fix, issue, error)
- Pattern matches existing taxonomy topics

## Steps

1. **Extract Keywords**
   - Parse the user's query for relevant terms
   - Identify domain-specific keywords (async, promise, hook, etc.)

2. **Search Taxonomy**
   ```bash
   uv run ~/.claude/skills/Learnings/Tools/search_learnings.py "query keywords"
   ```

3. **Review Results**
   - Tool returns top 5 matches with summaries
   - Each result includes:
     - Title
     - Tags/path in taxonomy
     - Problem summary
     - Solution summary

4. **Present to User**
   - If matches found: Present relevant learnings
   - If no matches: "No prior learnings found for this topic"

## Auto-Trigger Keywords
- bug, fix, issue, error
- debugging, troubleshoot
- "why is", "how do I fix"
- Stack trace patterns

## Example

User: "I'm getting a promise rejection error in my async hook"

1. Extract: [promise, rejection, async, hook]
2. Search taxonomy for matches
3. Present: "Found 2 relevant learnings about async promise handling..."
