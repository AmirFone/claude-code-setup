#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
Manual learning creation tool.
Creates a new learning entry and files it in the taxonomy tree.

Usage:
    add_learning.py --title "Title" --problem "Problem description" --solution "Solution" --tags "tag1,tag2" [--insight "Key insight"]
    add_learning.py --interactive  # Interactive mode with prompts
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


LEARNINGS_DIR = Path.home() / ".claude" / "history" / "learnings"
TAXONOMY_FILE = LEARNINGS_DIR / "taxonomy.json"


def load_taxonomy():
    """Load the taxonomy index."""
    if TAXONOMY_FILE.exists():
        with open(TAXONOMY_FILE, 'r') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "last_updated": None,
        "stats": {"total_learnings": 0, "total_branches": 0, "max_depth": 0},
        "tree": {},
        "proposed_branches": []
    }


def save_taxonomy(taxonomy):
    """Save the taxonomy index."""
    taxonomy["last_updated"] = datetime.now().isoformat()
    with open(TAXONOMY_FILE, 'w') as f:
        json.dump(taxonomy, f, indent=2)


def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def generate_learning_id():
    """Generate a unique learning ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"learning-{timestamp}"


def ensure_taxonomy_path(taxonomy, tags):
    """Ensure the taxonomy path exists and return the directory path."""
    tree = taxonomy["tree"]
    path_parts = []

    for tag in tags:
        tag_slug = slugify(tag)
        path_parts.append(tag_slug)

        if tag_slug not in tree:
            tree[tag_slug] = {
                "_meta": {"count": 0, "created": datetime.now().isoformat()},
                "_learnings": []
            }
            taxonomy["stats"]["total_branches"] += 1

        tree = tree[tag_slug]

    # Update depth stat
    if len(path_parts) > taxonomy["stats"]["max_depth"]:
        taxonomy["stats"]["max_depth"] = len(path_parts)

    # Create the directory
    dir_path = LEARNINGS_DIR / "/".join(path_parts)
    dir_path.mkdir(parents=True, exist_ok=True)

    return dir_path, path_parts


def create_learning_file(dir_path, learning_id, title, problem, solution, insight, tags):
    """Create the markdown learning file."""
    slug = slugify(title)
    file_path = dir_path / f"{slug}.md"

    # Handle duplicate filenames
    counter = 1
    while file_path.exists():
        file_path = dir_path / f"{slug}-{counter}.md"
        counter += 1

    content = f"""---
id: {learning_id}
title: "{title}"
created: {datetime.now().isoformat()}
source_session: manual
tags: [{", ".join(tags)}]
confidence: confirmed
---

# {title}

## Problem
{problem}

## Solution
{solution}

## Key Insight
{insight if insight else "N/A"}

## Related
- Manually created learning
"""

    with open(file_path, 'w') as f:
        f.write(content)

    return file_path


def update_taxonomy_index(taxonomy, path_parts, learning_id, title, file_path):
    """Update the taxonomy index with the new learning."""
    tree = taxonomy["tree"]

    # Navigate to the correct node
    for part in path_parts[:-1]:
        tree = tree[part]

    # Get the leaf node
    leaf = tree[path_parts[-1]]

    # Add learning reference
    if "_learnings" not in leaf:
        leaf["_learnings"] = []

    leaf["_learnings"].append({
        "id": learning_id,
        "title": title,
        "file": str(file_path.relative_to(LEARNINGS_DIR))
    })

    # Update counts
    leaf["_meta"]["count"] = len(leaf["_learnings"])
    taxonomy["stats"]["total_learnings"] += 1


def add_learning(title, problem, solution, tags, insight=None):
    """Add a new learning to the system."""
    # Load taxonomy
    taxonomy = load_taxonomy()

    # Generate ID
    learning_id = generate_learning_id()

    # Parse tags (comma-separated string to list)
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    else:
        tag_list = tags

    if not tag_list:
        tag_list = ["uncategorized"]

    # Ensure taxonomy path exists
    dir_path, path_parts = ensure_taxonomy_path(taxonomy, tag_list)

    # Create the learning file
    file_path = create_learning_file(
        dir_path, learning_id, title, problem, solution, insight, tag_list
    )

    # Update taxonomy index
    update_taxonomy_index(taxonomy, path_parts, learning_id, title, file_path)

    # Save taxonomy
    save_taxonomy(taxonomy)

    return learning_id, file_path


def interactive_mode():
    """Interactive mode for adding a learning."""
    print("=== Add New Learning ===\n")

    title = input("Title: ").strip()
    if not title:
        print("Error: Title is required")
        sys.exit(1)

    print("\nProblem (what went wrong or needed solving):")
    problem = input("> ").strip()

    print("\nSolution (how you fixed it):")
    solution = input("> ").strip()

    print("\nKey Insight (optional - the 'aha' moment):")
    insight = input("> ").strip() or None

    print("\nTags (comma-separated, e.g., 'debugging,async,promises'):")
    tags = input("> ").strip()

    return title, problem, solution, tags, insight


def main():
    parser = argparse.ArgumentParser(description="Add a new learning to the taxonomy")
    parser.add_argument('--title', help="Learning title")
    parser.add_argument('--problem', help="Problem description")
    parser.add_argument('--solution', help="Solution description")
    parser.add_argument('--tags', help="Comma-separated tags")
    parser.add_argument('--insight', help="Key insight (optional)")
    parser.add_argument('--interactive', '-i', action='store_true', help="Interactive mode")

    args = parser.parse_args()

    if args.interactive:
        title, problem, solution, tags, insight = interactive_mode()
    else:
        if not all([args.title, args.problem, args.solution, args.tags]):
            print("Error: --title, --problem, --solution, and --tags are required")
            print("Use --interactive for guided input")
            sys.exit(1)

        title = args.title
        problem = args.problem
        solution = args.solution
        tags = args.tags
        insight = args.insight

    try:
        learning_id, file_path = add_learning(title, problem, solution, tags, insight)
        print(f"\nLearning added successfully!")
        print(f"  ID: {learning_id}")
        print(f"  File: {file_path}")
    except Exception as e:
        print(f"Error adding learning: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
