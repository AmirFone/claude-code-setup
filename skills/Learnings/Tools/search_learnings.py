#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Search the learnings taxonomy for relevant past learnings.

Usage:
    python search_learnings.py "async promise rejection"
    python search_learnings.py --category debugging
    python search_learnings.py --list-categories
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


LEARNINGS_DIR = Path.home() / ".claude" / "history" / "learnings"
TAXONOMY_FILE = LEARNINGS_DIR / "taxonomy.json"


def load_taxonomy() -> Dict[str, Any]:
    """Load the taxonomy index."""
    if not TAXONOMY_FILE.exists():
        return {"version": "1.0", "tree": {}, "stats": {"total_learnings": 0}}
    return json.loads(TAXONOMY_FILE.read_text())


def extract_keywords(query: str) -> List[str]:
    """Extract search keywords from query."""
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                  'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                  'this', 'that', 'we', 'i', 'you', 'how', 'what', 'why', 'when', 'about'}

    words = re.findall(r'\b\w+\b', query.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]


def score_node(node_name: str, meta: Dict, keywords: List[str]) -> float:
    """Score a taxonomy node against keywords."""
    score = 0.0
    name_lower = node_name.lower()

    for kw in keywords:
        if kw in name_lower:
            score += 0.4
        # Partial match
        elif any(kw in name_lower or name_lower in kw for kw in keywords):
            score += 0.2

    # Boost nodes with more learnings
    count = meta.get("count", 0)
    if count > 0:
        score += min(count * 0.1, 0.3)

    return score


def score_learning(learning: Dict, keywords: List[str]) -> float:
    """Score a learning reference against keywords."""
    score = 0.0
    title_lower = learning.get("title", "").lower()

    for kw in keywords:
        if kw in title_lower:
            score += 0.3
        # Check for word parts
        title_words = title_lower.split()
        if any(kw in word or word in kw for word in title_words):
            score += 0.15

    return min(score, 1.0)


def search_tree(tree: Dict, keywords: List[str], path: List[str] = None) -> List[Dict]:
    """Recursively search the taxonomy tree."""
    if path is None:
        path = []

    results = []

    for node_name, node in tree.items():
        if node_name.startswith("_"):
            continue

        current_path = path + [node_name]
        meta = node.get("_meta", {})

        # Score this node
        node_score = score_node(node_name, meta, keywords)

        # If score is good enough, check learnings
        if node_score > 0.3:
            learnings = node.get("_learnings", [])
            for learning in learnings:
                learning_score = score_learning(learning, keywords)
                combined_score = (node_score + learning_score) / 2

                if combined_score > 0.4:
                    results.append({
                        "path": "/".join(current_path),
                        "title": learning.get("title", "Untitled"),
                        "file": learning.get("file", ""),
                        "relevance_score": round(combined_score, 2)
                    })

            # Recurse into children
            child_results = search_tree(node, keywords, current_path)
            results.extend(child_results)

        # Even if score is low, still check children (they might match better)
        elif node_score > 0.1:
            child_results = search_tree(node, keywords, current_path)
            results.extend(child_results)

    return results


def read_learning_file(file_path: str) -> Dict[str, str]:
    """Read a learning file and extract content."""
    full_path = LEARNINGS_DIR / file_path
    if not full_path.exists():
        return {}

    content = full_path.read_text()

    # Parse frontmatter
    result = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Parse YAML-like frontmatter
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
            result["content"] = parts[2].strip()

    return result


def format_results(results: List[Dict], show_content: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return "No matching learnings found."

    output = [f"Found {len(results)} relevant learning(s):\n"]

    for i, result in enumerate(results, 1):
        output.append(f"{i}. **{result['title']}**")
        output.append(f"   Path: {result['path']}")
        output.append(f"   Relevance: {int(result['relevance_score'] * 100)}%")

        if show_content and result.get("file"):
            learning = read_learning_file(result["file"])
            if learning.get("content"):
                # Show first 200 chars of content
                preview = learning["content"][:200]
                if len(learning["content"]) > 200:
                    preview += "..."
                output.append(f"   Preview: {preview}")

        output.append("")

    return "\n".join(output)


def list_categories(tree: Dict, prefix: str = "") -> List[str]:
    """List all categories in the taxonomy."""
    categories = []

    for node_name, node in tree.items():
        if node_name.startswith("_"):
            continue

        path = f"{prefix}/{node_name}" if prefix else node_name
        meta = node.get("_meta", {})
        count = meta.get("count", 0)
        learnings_count = len(node.get("_learnings", []))

        categories.append(f"{path} ({learnings_count} learnings)")

        # Recurse
        child_categories = list_categories(node, path)
        categories.extend(child_categories)

    return categories


def main():
    parser = argparse.ArgumentParser(description="Search learnings taxonomy")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--list-categories", "-l", action="store_true", help="List all categories")
    parser.add_argument("--show-content", "-s", action="store_true", help="Show learning content")
    parser.add_argument("--max-results", "-n", type=int, default=5, help="Max results")

    args = parser.parse_args()

    taxonomy = load_taxonomy()

    if args.list_categories:
        categories = list_categories(taxonomy.get("tree", {}))
        if categories:
            print("Taxonomy categories:\n")
            for cat in categories:
                print(f"  - {cat}")
        else:
            print("No categories yet. Start saving learnings to build the taxonomy!")
        return

    if not args.query:
        print("Usage: search_learnings.py 'your search query'")
        print("       search_learnings.py --list-categories")
        return

    query = " ".join(args.query)
    keywords = extract_keywords(query)

    if not keywords:
        print("No searchable keywords found in query.")
        return

    # Search the tree
    results = search_tree(taxonomy.get("tree", {}), keywords)

    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Limit results
    results = results[:args.max_results]

    # Format and print
    print(format_results(results, args.show_content))


if __name__ == "__main__":
    main()
