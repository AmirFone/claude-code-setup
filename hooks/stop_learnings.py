#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Learning detection hook for Claude Code sessions.
Detects potential learnings at session end and batches them for confirmation.

This runs on Stop events and:
1. Reads the session transcript
2. Detects learning-worthy moments (problem-solution pairs)
3. Proposes taxonomy placement
4. Writes to pending/ for user confirmation
"""

import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


# Learning indicators with weights
LEARNING_INDICATORS = [
    (r"figured out", 0.3),
    (r"root cause", 0.4),
    (r"the issue was", 0.35),
    (r"turned out", 0.25),
    (r"realized that", 0.3),
    (r"the fix is", 0.35),
    (r"solved by", 0.35),
    (r"learned that", 0.4),
    (r"discovered that", 0.35),
    (r"the problem was", 0.35),
    (r"solution is", 0.35),
    (r"key insight", 0.4),
    (r"important to note", 0.3),
    (r"mistake was", 0.35),
    (r"working now", 0.25),
]

# Debugging triggers (for auto-retrieval later)
DEBUGGING_TRIGGERS = [
    'bug', 'fix', 'issue', 'broken', 'error', 'failed',
    'crash', 'debug', 'wrong', 'unexpected'
]

# Taxonomy top-level categories for auto-classification
TAXONOMY_CATEGORIES = {
    "debugging": ["bug", "fix", "error", "issue", "problem", "crash", "debug", "broken"],
    "architecture": ["design", "pattern", "structure", "component", "module", "system", "refactor"],
    "tools": ["git", "npm", "docker", "cli", "command", "tool", "script"],
    "performance": ["slow", "fast", "optimize", "memory", "cache", "speed"],
    "security": ["auth", "token", "permission", "secure", "vulnerability", "credential"],
    "testing": ["test", "spec", "mock", "assert", "coverage"],
    "deployment": ["deploy", "build", "ci", "cd", "release", "production"],
    "database": ["sql", "query", "migration", "schema", "database", "db"],
    "api": ["endpoint", "request", "response", "rest", "graphql", "api"],
    "frontend": ["ui", "css", "react", "component", "render", "dom"],
}


def get_local_timestamp() -> str:
    """Get formatted local timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def content_to_text(content) -> str:
    """Convert Claude content to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict):
                if c.get("text"):
                    parts.append(c["text"])
                elif c.get("content"):
                    parts.append(content_to_text(c["content"]))
        return " ".join(parts).strip()
    return ""


def calculate_learning_score(text: str) -> Tuple[float, List[str]]:
    """Calculate learning potential score and matched indicators."""
    score = 0.0
    matched = []

    text_lower = text.lower()

    for pattern, weight in LEARNING_INDICATORS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            score += weight
            matched.append(pattern)

    return min(score, 1.0), matched


def propose_taxonomy(text: str) -> str:
    """Propose taxonomy path based on content analysis."""
    text_lower = text.lower()

    # Score each category
    scores = {}
    for category, keywords in TAXONOMY_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score

    if not scores:
        return "general"

    # Get top category
    top_category = max(scores, key=scores.get)
    return top_category


def extract_problem_solution(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Attempt to extract problem and solution from text."""
    problem = None
    solution = None

    # Look for problem patterns
    problem_patterns = [
        r"(?:the\s+)?(?:problem|issue|bug)\s+(?:was|is)[:\s]+(.+?)(?:\.|$)",
        r"(?:error|failed)(?::\s*|\s+)(.+?)(?:\.|$)",
    ]

    for pattern in problem_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            problem = match.group(1).strip()[:200]
            break

    # Look for solution patterns
    solution_patterns = [
        r"(?:the\s+)?(?:fix|solution)\s+(?:was|is)[:\s]+(.+?)(?:\.|$)",
        r"(?:fixed|solved)\s+(?:by|with)[:\s]+(.+?)(?:\.|$)",
        r"(?:figured out|realized)[:\s]+(.+?)(?:\.|$)",
    ]

    for pattern in solution_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            solution = match.group(1).strip()[:200]
            break

    return problem, solution


def extract_code_snippet(text: str) -> Optional[str]:
    """Extract relevant code snippet if present."""
    # Look for code blocks
    match = re.search(r"```[\w]*\n([\s\S]+?)```", text)
    if match:
        code = match.group(1).strip()
        # Limit size
        if len(code) < 500:
            return code
    return None


def generate_title(text: str, problem: Optional[str], solution: Optional[str]) -> str:
    """Generate a concise title for the learning."""
    if solution:
        # Clean and truncate solution for title
        title = re.sub(r"[^\w\s-]", "", solution)
        words = title.split()[:6]
        return " ".join(words).title()

    if problem:
        title = re.sub(r"[^\w\s-]", "", problem)
        words = title.split()[:6]
        return f"Fix: " + " ".join(words).title()

    # Fallback: extract first meaningful sentence
    sentences = text.split(".")
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            words = s.split()[:6]
            return " ".join(words).title()

    return "Development Learning"


def read_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Read and parse transcript file."""
    messages = []
    try:
        path = Path(transcript_path)
        if not path.exists():
            return messages

        content = path.read_text()
        for line in content.strip().split("\n"):
            if line.strip():
                try:
                    entry = json.loads(line)
                    messages.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return messages


def detect_learnings(transcript_path: str, session_id: str) -> List[Dict[str, Any]]:
    """Detect potential learnings from session transcript."""
    messages = read_transcript(transcript_path)
    learnings = []

    # Process assistant messages for learning indicators
    for i, entry in enumerate(messages):
        if entry.get("type") != "assistant":
            continue

        content = entry.get("message", {}).get("content", [])
        text = content_to_text(content)

        if not text or len(text) < 50:
            continue

        # Calculate learning score
        score, matched_indicators = calculate_learning_score(text)

        # Only consider high-confidence learnings
        if score < 0.6:
            continue

        # Extract structured information
        problem, solution = extract_problem_solution(text)
        code_snippet = extract_code_snippet(text)
        taxonomy = propose_taxonomy(text)
        title = generate_title(text, problem, solution)

        learning = {
            "id": f"pending-{uuid.uuid4().hex[:8]}",
            "title": title,
            "auto_detected": True,
            "detection_indicators": matched_indicators,
            "proposed_taxonomy": taxonomy,
            "problem": problem or "Not explicitly stated",
            "solution": solution or "See context below",
            "code_snippet": code_snippet,
            "confidence": round(score, 2),
            "context_from_session": text[:500] + "..." if len(text) > 500 else text,
            "message_index": i
        }

        learnings.append(learning)

    # Deduplicate by similarity (simple title comparison)
    seen_titles = set()
    unique_learnings = []
    for learning in learnings:
        title_key = learning["title"].lower()[:30]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_learnings.append(learning)

    return unique_learnings[:5]  # Limit to 5 learnings per session


def save_pending_learnings(session_id: str, learnings: List[Dict[str, Any]]) -> Path:
    """Save pending learnings for user review."""
    claude_dir = Path.home() / ".claude"
    pending_dir = claude_dir / "history" / "learnings" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    pending_file = pending_dir / f"{session_id}_pending.json"

    data = {
        "session_id": session_id,
        "captured_at": datetime.now().isoformat() + "Z",
        "pending_learnings": learnings,
        "proposed_new_branches": []
    }

    pending_file.write_text(json.dumps(data, indent=2))
    return pending_file


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        payload = json.loads(stdin_data)
        session_id = payload.get("session_id", "unknown")
        transcript_path = payload.get("transcript_path", "")

        if not transcript_path:
            sys.exit(0)

        # Detect potential learnings
        learnings = detect_learnings(transcript_path, session_id)

        if learnings:
            # Save to pending
            pending_file = save_pending_learnings(session_id, learnings)

            # Notify user
            print(f"\n{len(learnings)} potential learning(s) detected.")
            for i, learning in enumerate(learnings, 1):
                print(f"  {i}. {learning['title']} ({learning['proposed_taxonomy']})")
            print(f"\nReview with: \"review my pending learnings\"")

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Learning detection error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
