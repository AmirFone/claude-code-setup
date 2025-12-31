# SpawnParallelAgents Workflow

**Launches multiple agents in parallel for grunt work and batch processing.**

## When to Use

User says:
- "Launch a bunch of agents to do X"
- "Spin up agents to handle Y"
- "Run multiple agents on Z"

**KEY DISTINCTION**: This is for generic parallel work, NOT custom agents. For custom agents with unique personalities, use CreateCustomAgent workflow.

## The Workflow

### Step 1: Determine Requirements

Extract from user's request:
- How many agents? (Default: 3-5)
- What's the task for each?
- Are tasks identical or need variation?

### Step 2: Choose Agent Type and Model

| Work Type | subagent_type | Model | Why |
|-----------|---------------|-------|-----|
| Grunt work | `Intern` | `haiku` | Fast, cheap, parallel |
| Analysis | `general-purpose` | `sonnet` | Balanced |
| Deep thinking | `general-purpose` | `opus` | Maximum quality |

### Step 3: Launch in Single Message

**CRITICAL: Use a SINGLE message with MULTIPLE Task tool calls.**

```typescript
// Example: 3 parallel research tasks
Task({
  description: "Research agent 1",
  prompt: "Research topic A and summarize key findings...",
  subagent_type: "Intern",
  model: "haiku"
})
Task({
  description: "Research agent 2",
  prompt: "Research topic B and summarize key findings...",
  subagent_type: "Intern",
  model: "haiku"
})
Task({
  description: "Research agent 3",
  prompt: "Research topic C and summarize key findings...",
  subagent_type: "Intern",
  model: "haiku"
})
```

### Step 4: Collect Results

Wait for all agents to complete, then synthesize their outputs:

```typescript
// Results come back as each agent completes
// Combine and summarize for user
```

## Task Distribution Patterns

### Pattern 1: Same Task, Different Inputs
```
"Research these 5 competitors"
→ Launch 5 agents, each researching 1 competitor
```

### Pattern 2: Different Perspectives
```
"Get multiple views on this decision"
→ Launch 3-5 agents with prompts emphasizing different angles
```

### Pattern 3: Divide and Conquer
```
"Analyze this large codebase"
→ Launch agents for different directories/modules
```

## Model Selection Guide

| Task Complexity | Model | Cost | Speed |
|-----------------|-------|------|-------|
| Simple extraction | `haiku` | $$ | Very Fast |
| Standard analysis | `sonnet` | $$$ | Fast |
| Complex reasoning | `opus` | $$$$ | Slower |

**Rule of thumb**: Start with `haiku`, escalate only if quality insufficient.

## Example Prompts

### Batch Research
```
User: "Research the top 5 AI companies and summarize each"

AI: Launches 5 parallel Intern agents with haiku model
- Agent 1: OpenAI
- Agent 2: Anthropic
- Agent 3: Google DeepMind
- Agent 4: Microsoft
- Agent 5: Meta AI
```

### Multi-Perspective Analysis
```
User: "Get different perspectives on this architecture"

AI: Launches 3 parallel agents
- Agent 1: Performance perspective
- Agent 2: Security perspective
- Agent 3: Maintainability perspective
```

## Common Mistakes

**WRONG: Sequential instead of parallel**
```typescript
// WRONG - launches one at a time, slow
await Task({ prompt: "Task 1" })
await Task({ prompt: "Task 2" })
```

**RIGHT: Parallel in single message**
```typescript
// CORRECT - all launch simultaneously
Task({ prompt: "Task 1" })
Task({ prompt: "Task 2" })
Task({ prompt: "Task 3" })
// All in same message
```

## When NOT to Use This Workflow

- For custom agents with unique personalities → Use CreateCustomAgent
- For named agents (Intern, Architect, etc.) → Use direct Task calls
- For single specialized task → Just use one agent

## Expected Outcome

- Multiple agents working in parallel
- Results collected and synthesized
- Faster completion than sequential processing
