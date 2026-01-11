#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Review and confirm pending learnings.

Usage:
    python review_pending.py              # List all pending
    python review_pending.py --confirm 1  # Confirm learning #1
    python review_pending.py --dismiss 2  # Dismiss learning #2
    python review_pending.py --confirm-all  # Confirm all pending
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


LEARNINGS_DIR = Path.home() / ".claude" / "history" / "learnings"
PENDING_DIR = LEARNINGS_DIR / "pending"
TAXONOMY_FILE = LEARNINGS_DIR / "taxonomy.json"


def get_pending_files() -> List[Path]:
    """Get all pending learning files."""
    if not PENDING_DIR.exists():
        return []
    return sorted(PENDING_DIR.glob("*_pending.json"), key=lambda f: f.stat().st_mtime, reverse=True)


def load_all_pending() -> List[Dict[str, Any]]:
    """Load all pending learnings from all files."""
    all_pending = []

    for pending_file in get_pending_files():
        try:
            data = json.loads(pending_file.read_text())
            session_id = data.get("session_id", "unknown")
            captured_at = data.get("captured_at", "")

            for learning in data.get("pending_learnings", []):
                learning["_source_file"] = str(pending_file)
                learning["_session_id"] = session_id
                learning["_captured_at"] = captured_at
                all_pending.append(learning)
        except Exception:
            continue

    return all_pending


def load_taxonomy() -> Dict[str, Any]:
    """Load the taxonomy index."""
    if not TAXONOMY_FILE.exists():
        return {
            "version": "1.0",
            "last_updated": None,
            "stats": {"total_learnings": 0, "total_branches": 0, "max_depth": 0},
            "tree": {},
            "proposed_branches": []
        }
    return json.loads(TAXONOMY_FILE.read_text())


def save_taxonomy(taxonomy: Dict[str, Any]) -> None:
    """Save the taxonomy index."""
    taxonomy["last_updated"] = datetime.now().isoformat() + "Z"
    TAXONOMY_FILE.write_text(json.dumps(taxonomy, indent=2))


def ensure_taxonomy_path(taxonomy: Dict, path: str) -> Dict:
    """Ensure a taxonomy path exists, creating nodes as needed."""
    parts = path.split("/")
    current = taxonomy["tree"]

    for part in parts:
        if part not in current:
            current[part] = {
                "_meta": {"count": 0, "created": datetime.now().isoformat()},
                "_learnings": []
            }
        current = current[part]

    return current


def generate_learning_id() -> str:
    """Generate a unique learning ID."""
    now = datetime.now()
    return f"learning-{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"


def slugify(text: str) -> str:
    """Convert text to a slug for filename."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')
    return slug[:60]


def create_learning_file(learning: Dict, taxonomy_path: str) -> Path:
    """Create the actual learning markdown file."""
    learning_id = generate_learning_id()
    slug = slugify(learning.get("title", "untitled"))
    filename = f"{slug}.md"

    # Create directory for taxonomy path
    dir_path = LEARNINGS_DIR / taxonomy_path.replace("/", "/")
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / filename

    # Build markdown content
    content = f"""---
id: {learning_id}
title: "{learning.get('title', 'Untitled')}"
created: {datetime.now().isoformat()}Z
source_session: {learning.get('_session_id', 'unknown')}
tags: [{taxonomy_path}]
confidence: confirmed
---

# {learning.get('title', 'Untitled')}

## Problem

{learning.get('problem', 'Not specified')}

## Solution

{learning.get('solution', 'Not specified')}

"""

    if learning.get("code_snippet"):
        content += f"""## Code

```
{learning['code_snippet']}
```

"""

    content += f"""## Key Insight

{learning.get('context_from_session', '')[:300]}...

## Related

- Source session: {learning.get('_session_id', 'unknown')}
- Captured: {learning.get('_captured_at', '')}

---
*Learning confirmed and saved*
"""

    file_path.write_text(content)
    return file_path


def confirm_learning(learning: Dict) -> Optional[Path]:
    """Confirm a learning and add it to the taxonomy."""
    taxonomy = load_taxonomy()
    taxonomy_path = learning.get("proposed_taxonomy", "general")

    # Ensure path exists
    node = ensure_taxonomy_path(taxonomy, taxonomy_path)

    # Create the learning file
    file_path = create_learning_file(learning, taxonomy_path)
    relative_path = str(file_path.relative_to(LEARNINGS_DIR))

    # Add to taxonomy
    learning_ref = {
        "id": generate_learning_id(),
        "title": learning.get("title", "Untitled"),
        "file": relative_path
    }
    node["_learnings"].append(learning_ref)
    node["_meta"]["count"] = len(node["_learnings"])

    # Update stats
    taxonomy["stats"]["total_learnings"] = taxonomy["stats"].get("total_learnings", 0) + 1

    save_taxonomy(taxonomy)
    return file_path


def remove_from_pending(learning: Dict) -> None:
    """Remove a learning from its pending file."""
    source_file = Path(learning.get("_source_file", ""))
    if not source_file.exists():
        return

    data = json.loads(source_file.read_text())
    data["pending_learnings"] = [
        l for l in data.get("pending_learnings", [])
        if l.get("id") != learning.get("id")
    ]

    if not data["pending_learnings"]:
        # Delete the file if empty
        source_file.unlink()
    else:
        source_file.write_text(json.dumps(data, indent=2))


def format_pending_list(pending: List[Dict]) -> str:
    """Format pending learnings for display."""
    if not pending:
        return "No pending learnings to review."

    output = [f"Found {len(pending)} pending learning(s):\n"]

    for i, learning in enumerate(pending, 1):
        output.append(f"{i}. **{learning.get('title', 'Untitled')}**")
        output.append(f"   Category: {learning.get('proposed_taxonomy', 'general')}")
        output.append(f"   Confidence: {int(learning.get('confidence', 0) * 100)}%")
        output.append(f"   Indicators: {', '.join(learning.get('detection_indicators', []))}")

        problem = learning.get("problem", "")
        if problem and problem != "Not explicitly stated":
            output.append(f"   Problem: {problem[:100]}...")

        output.append("")

    output.append("Commands:")
    output.append("  --confirm N    Confirm learning #N")
    output.append("  --dismiss N    Dismiss learning #N")
    output.append("  --confirm-all  Confirm all pending")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Review pending learnings")
    parser.add_argument("--confirm", type=int, help="Confirm learning by number")
    parser.add_argument("--dismiss", type=int, help="Dismiss learning by number")
    parser.add_argument("--confirm-all", action="store_true", help="Confirm all pending")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    pending = load_all_pending()

    if args.confirm:
        if args.confirm < 1 or args.confirm > len(pending):
            print(f"Invalid learning number. Choose 1-{len(pending)}")
            sys.exit(1)

        learning = pending[args.confirm - 1]
        file_path = confirm_learning(learning)
        remove_from_pending(learning)
        print(f"Confirmed: {learning.get('title')}")
        print(f"Saved to: {file_path}")

    elif args.dismiss:
        if args.dismiss < 1 or args.dismiss > len(pending):
            print(f"Invalid learning number. Choose 1-{len(pending)}")
            sys.exit(1)

        learning = pending[args.dismiss - 1]
        remove_from_pending(learning)
        print(f"Dismissed: {learning.get('title')}")

    elif args.confirm_all:
        for learning in pending:
            file_path = confirm_learning(learning)
            remove_from_pending(learning)
            print(f"Confirmed: {learning.get('title')}")
        print(f"\nConfirmed {len(pending)} learning(s)")

    elif args.json:
        print(json.dumps(pending, indent=2))

    else:
        print(format_pending_list(pending))


if __name__ == "__main__":
    main()
