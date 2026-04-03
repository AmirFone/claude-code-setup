# Company Research Protocol

Research the target company's hiring culture before touching the resume. Every resume change should be traceable to a specific hiring signal.

## Search Queries

Run these five web searches, substituting `[Company]` with the target company name:

1. `[Company] software engineer interview Reddit`
2. `[Company] resume tips Reddit`
3. `[Company] what they look for hiring`
4. `[Company] interview process Glassdoor`
5. `[Company] engineering culture values`

For non-engineering roles, adapt the first query to match the role domain (e.g., "product manager interview" instead of "software engineer interview").

### Supplementary Queries (if initial results are thin)

- `[Company] hiring manager advice`
- `[Company] what makes a good candidate`
- `site:teamblind.com [Company] resume`
- `[Company] careers blog engineering`

## Signal Extraction Framework

From search results, extract three categories of signals:

### 1. Valued Signals
Traits, experiences, or keywords that interviewers and hiring managers consistently mention as important.

**Look for patterns like:**
- What interviewers say they screen for ("We care about X")
- What successful candidates report emphasizing
- Recurring themes across multiple sources
- Specific metrics or evidence types the company values

**Company-specific examples:**
| Company | Known Valued Signals |
|---------|---------------------|
| Google | Scale numbers, system design depth, data-driven decisions, impact quantification |
| Stripe | API design taste, developer experience empathy, clear writing |
| Meta | Speed of execution, "move fast", impact at scale, cross-functional collaboration |
| Amazon | Leadership principles language, customer obsession, data-backed decisions, ownership |
| Apple | Craft and polish, attention to detail, secrecy-compatible communication |
| OpenAI | Speed, comfort with ambiguity, research-to-production, safety awareness |

### 2. Red Flags to Avoid
Anything the community says gets resumes deprioritized or rejected.

**Common patterns:**
- Overuse of buzzwords without substance
- Listing technologies without demonstrating depth
- Generic objectives or summaries
- Formatting that doesn't match company culture (e.g., overly creative for a conservative company)
- Claims that can't be backed up in an interview

### 3. Cultural Language
Terms the company uses internally that would resonate with reviewers.

**How to identify:**
- Company blog posts and engineering publications
- Mission statements and values pages
- Language patterns in the job description itself
- Terminology from employee interviews and talks
- Internal jargon that appears in public communications

## Output Format

Present research findings in this exact structure before proposing any resume changes:

```markdown
### Company Hiring Signals

**Sources reviewed:**
- [URL 1] - [brief description of source]
- [URL 2] - [brief description of source]
- ...

**What they value:**
- [Signal 1] - [evidence/source]
- [Signal 2] - [evidence/source]
- ...

**What to avoid:**
- [Red flag 1] - [why]
- [Red flag 2] - [why]
- ...

**Cultural language to weave in:**
- "[Term/phrase 1]" - [where it's used, what it signals]
- "[Term/phrase 2]" - [where it's used, what it signals]
- ...
```

## Using Signals in Resume Changes

Every change in Part 2 (Change Log) must cite which signal drove it:

```
- "built REST API" → "designed and shipped developer-facing REST API serving 50K req/s"
  - Why: Stripe values API design taste and developer experience (Signal: API design depth)
```

If a change cannot be traced to a specific signal or JD keyword, question whether the change is necessary.

## When Research Yields Little

For smaller or less-discussed companies:

1. Lean more heavily on the job description itself for cultural signals
2. Look at the company's engineering blog, GitHub repos, or tech talks
3. Check LinkedIn posts from engineering leadership
4. Default to industry-standard signals for the company's sector
5. Note in the output: "Limited public hiring signal data available. Changes driven primarily by JD keyword alignment."
