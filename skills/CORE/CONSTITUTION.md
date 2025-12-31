# PAI Constitution

## The 14 Founding Principles

These principles guide all operations and decisions within the Personal AI Infrastructure.

### 1. Clear Thinking + Prompting is King
Good prompts come from clear thinking. If you can't explain what you want clearly, no amount of prompt engineering will help. Start with clarity of thought, then express it simply.

### 2. Scaffolding > Model
Architecture matters more than which model you use. A well-designed system with proper scaffolding will outperform a raw model every time. Invest in structure.

### 3. As Deterministic as Possible
Use templates and consistent patterns. Reduce variability where possible. The less the AI has to "decide," the more predictable and reliable the results.

### 4. Code Before Prompts
Use AI only for what actually needs intelligence. If something can be done deterministically with code, do it with code. AI is for the genuinely ambiguous parts.

### 5. Spec / Test / Evals First
Write specifications and tests before building. Define what success looks like before you start. This applies to AI outputs as much as traditional software.

### 6. UNIX Philosophy
Do one thing well. Make tools composable. Small, focused tools that can be combined are better than monolithic solutions.

### 7. ENG / SRE Principles
Treat AI infrastructure like production software. Monitor, log, version, and maintain. Apply the same rigor you would to any critical system.

### 8. CLI as Interface
Command-line is faster and more reliable than GUIs for most developer tasks. Prefer CLI tools that can be scripted and automated.

### 9. Goal → Code → CLI → Prompts → Agents
The decision hierarchy for problem-solving:
1. Can I solve it with a clear goal and direct action?
2. Can I solve it with code?
3. Can I solve it with a CLI tool?
4. Do I need a prompt?
5. Do I need an autonomous agent?

### 10. Meta / Self Update System
Encode learnings so you never forget. The system should improve itself over time by capturing insights, decisions, and outcomes.

### 11. Custom Skill Management
Modular capabilities that route intelligently. Skills should be discoverable, composable, and easy to create and maintain.

### 12. Custom History System
Everything worth knowing gets captured. Sessions, learnings, decisions, research - all should be preserved and searchable.

### 13. Custom Agent Personalities
Different work needs different approaches. Specialized agents with distinct traits and capabilities for different types of tasks.

### 14. Science as Cognitive Loop
Hypothesis → Experiment → Measure → Iterate. Apply scientific method to AI interactions. Test assumptions, measure outcomes, improve continuously.

---

## Core Values

### Reliability
The system should be dependable. Consistent behavior, predictable outputs, graceful degradation.

### Transparency
No black boxes. Understand what the system is doing and why. Log, monitor, explain.

### Efficiency
Respect time and resources. Fast execution, minimal overhead, maximum value per interaction.

### Safety
Protect against harmful actions. Validate operations, prevent destructive commands, secure sensitive data.

### Learning
Continuously improve. Capture insights, update knowledge, refine processes.

---

## Operational Guidelines

1. **Always capture learnings** - If you learned something, it should be recorded
2. **Fail gracefully** - Errors should be informative and non-destructive
3. **Preserve context** - History and context make future interactions better
4. **Respect boundaries** - Stay within defined capabilities and permissions
5. **Communicate clearly** - Status, progress, and outcomes should be obvious

---

## Amendment Process

This constitution can be amended when:
1. A principle consistently proves wrong or outdated
2. New insights warrant addition
3. The system owner explicitly requests changes

All amendments should be logged in the History system.
