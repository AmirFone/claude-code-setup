#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Update terminal tab title with task context.
UserPromptSubmit hook.

Migrated from ~/.config/pai/hooks/update-tab-titles.ts
"""

import json
import sys


# Common filler words to remove
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
    'my', 'your', 'please', 'help', 'want', 'need', 'like', 'just'
}


def set_tab_title(title: str) -> None:
    """Set terminal tab and window title using OSC escape sequences."""
    # OSC escape sequences for terminal tab and window titles
    tab_escape = f"\x1b]1;{title}\x07"
    window_escape = f"\x1b]2;{title}\x07"

    sys.stderr.write(tab_escape)
    sys.stderr.write(window_escape)
    sys.stderr.flush()


def extract_task_keywords(prompt: str) -> str:
    """Extract significant keywords from prompt for title."""
    import re

    # Clean and tokenize
    cleaned = re.sub(r'[^\w\s-]', ' ', prompt.lower())
    words = cleaned.split()

    # Filter out stop words and short words
    keywords = [w for w in words if len(w) > 2 and w not in STOP_WORDS]

    # Take first 4 significant words
    keywords = keywords[:4]

    if not keywords:
        return "Working"

    # Capitalize first word
    keywords[0] = keywords[0].capitalize()

    return " ".join(keywords)


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        payload = json.loads(stdin_data)
        prompt = payload.get("prompt", "") or payload.get("message", "")

        if not prompt or len(prompt) < 3:
            sys.exit(0)

        # Generate quick title from keywords
        keywords = extract_task_keywords(prompt)
        set_tab_title(f"Claude: {keywords}")

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Tab title update error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
