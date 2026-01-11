#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
Taxonomy rebalancing tool.
Analyzes the taxonomy tree and suggests reorganization for better navigation.

Triggers:
- Depth > 5 levels -> suggest flatten
- Branch > 10 siblings -> suggest group
- Branch < 2 learnings -> suggest merge

Usage:
    rebalance.py --analyze              # Show suggestions
    rebalance.py --apply SUGGESTION_ID  # Apply a specific suggestion
    rebalance.py --history              # Show rebalance history
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


LEARNINGS_DIR = Path.home() / ".claude" / "history" / "learnings"
TAXONOMY_FILE = LEARNINGS_DIR / "taxonomy.json"
META_DIR = Path.home() / ".claude" / "history" / "meta"
HISTORY_FILE = META_DIR / "rebalance-history.json"


# Thresholds for suggestions
MAX_DEPTH = 5
MAX_SIBLINGS = 10
MIN_LEARNINGS = 2


def load_taxonomy():
    """Load the taxonomy index."""
    if TAXONOMY_FILE.exists():
        with open(TAXONOMY_FILE, 'r') as f:
            return json.load(f)
    return {"tree": {}, "stats": {}}


def save_taxonomy(taxonomy):
    """Save the taxonomy index."""
    taxonomy["last_updated"] = datetime.now().isoformat()
    with open(TAXONOMY_FILE, 'w') as f:
        json.dump(taxonomy, f, indent=2)


def load_history():
    """Load rebalance history."""
    META_DIR.mkdir(parents=True, exist_ok=True)
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"changes": []}


def save_history(history):
    """Save rebalance history."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def analyze_tree(tree, path=None, depth=0):
    """
    Recursively analyze the taxonomy tree for rebalancing opportunities.
    Returns list of suggestions.
    """
    if path is None:
        path = []

    suggestions = []

    # Skip metadata keys
    child_keys = [k for k in tree.keys() if not k.startswith('_')]

    # Check depth
    if depth > MAX_DEPTH:
        suggestions.append({
            "type": "flatten",
            "path": "/".join(path),
            "reason": f"Depth ({depth}) exceeds maximum ({MAX_DEPTH})",
            "action": f"Consider flattening branches under '{'/'.join(path)}'"
        })

    # Check siblings count
    if len(child_keys) > MAX_SIBLINGS:
        suggestions.append({
            "type": "group",
            "path": "/".join(path) if path else "root",
            "reason": f"Too many siblings ({len(child_keys)}) at this level",
            "action": f"Consider grouping related branches under '{'/'.join(path) or 'root'}'"
        })

    # Check for sparse branches
    for key in child_keys:
        child = tree[key]
        child_path = path + [key]

        # Get learning count
        learning_count = len(child.get("_learnings", []))
        has_children = any(not k.startswith('_') for k in child.keys())

        if not has_children and learning_count < MIN_LEARNINGS and learning_count > 0:
            suggestions.append({
                "type": "merge",
                "path": "/".join(child_path),
                "reason": f"Sparse branch with only {learning_count} learning(s)",
                "action": f"Consider merging '{'/'.join(child_path)}' with a sibling or parent"
            })

        # Recurse into children
        if has_children:
            child_suggestions = analyze_tree(child, child_path, depth + 1)
            suggestions.extend(child_suggestions)

    return suggestions


def print_suggestions(suggestions):
    """Print suggestions in a readable format."""
    if not suggestions:
        print("No rebalancing suggestions. Your taxonomy is well-organized!")
        return

    print(f"Found {len(suggestions)} suggestion(s):\n")

    for i, suggestion in enumerate(suggestions, 1):
        print(f"[{i}] {suggestion['type'].upper()}")
        print(f"    Path: {suggestion['path']}")
        print(f"    Reason: {suggestion['reason']}")
        print(f"    Action: {suggestion['action']}")
        print()


def apply_flatten(taxonomy, path):
    """
    Flatten a deep branch by moving all sub-learnings up one level.
    """
    parts = path.split('/') if path else []
    tree = taxonomy["tree"]

    # Navigate to parent
    parent = tree
    for part in parts[:-1]:
        parent = parent.get(part, {})

    if not parts:
        return False, "Cannot flatten root"

    target_key = parts[-1]
    target = parent.get(target_key, {})

    # Collect all learnings from children
    collected_learnings = []

    def collect_learnings(node):
        if "_learnings" in node:
            collected_learnings.extend(node["_learnings"])
        for key, child in node.items():
            if not key.startswith('_') and isinstance(child, dict):
                collect_learnings(child)

    collect_learnings(target)

    # Flatten: keep only _meta and _learnings
    parent[target_key] = {
        "_meta": target.get("_meta", {"count": 0}),
        "_learnings": collected_learnings
    }
    parent[target_key]["_meta"]["count"] = len(collected_learnings)

    return True, f"Flattened {len(collected_learnings)} learnings under {path}"


def apply_suggestion(suggestion_id, suggestions, taxonomy):
    """Apply a specific suggestion."""
    if suggestion_id < 1 or suggestion_id > len(suggestions):
        return False, f"Invalid suggestion ID: {suggestion_id}"

    suggestion = suggestions[suggestion_id - 1]
    suggestion_type = suggestion["type"]
    path = suggestion["path"]

    if suggestion_type == "flatten":
        return apply_flatten(taxonomy, path)
    elif suggestion_type == "group":
        return False, "Group suggestions require manual intervention. Review the branches and group related items."
    elif suggestion_type == "merge":
        return False, "Merge suggestions require manual intervention. Review and merge related branches."
    else:
        return False, f"Unknown suggestion type: {suggestion_type}"


def record_change(history, action, details):
    """Record a rebalancing change to history."""
    history["changes"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })


def show_history():
    """Display rebalance history."""
    history = load_history()

    if not history["changes"]:
        print("No rebalancing history yet.")
        return

    print("Rebalance History:\n")
    for change in history["changes"][-10:]:  # Last 10 changes
        print(f"  {change['timestamp']}")
        print(f"    Action: {change['action']}")
        print(f"    Details: {change['details']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Taxonomy rebalancing tool")
    parser.add_argument('--analyze', '-a', action='store_true', help="Analyze and show suggestions")
    parser.add_argument('--apply', type=int, help="Apply suggestion by ID")
    parser.add_argument('--history', '-H', action='store_true', help="Show rebalance history")

    args = parser.parse_args()

    if args.history:
        show_history()
        return

    taxonomy = load_taxonomy()
    suggestions = analyze_tree(taxonomy.get("tree", {}))

    if args.analyze or not args.apply:
        print_suggestions(suggestions)
        if suggestions:
            print("To apply a suggestion: rebalance.py --apply <number>")
        return

    if args.apply:
        if not suggestions:
            print("No suggestions to apply.")
            return

        success, message = apply_suggestion(args.apply, suggestions, taxonomy)

        if success:
            save_taxonomy(taxonomy)
            history = load_history()
            record_change(history, f"Applied suggestion {args.apply}", message)
            save_history(history)
            print(f"Success: {message}")
        else:
            print(f"Note: {message}")


if __name__ == '__main__':
    main()
