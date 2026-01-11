#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Voice notification for subagent completions.
Sends completion messages to voice server with personality-specific delivery.

Migrated from ~/.config/pai/hooks/subagent-stop-hook-voice.ts
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import httpx
except ImportError:
    httpx = None

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

try:
    from prosody_enhancer import clean_for_speech, get_voice_id
except ImportError:
    def clean_for_speech(msg): return msg
    def get_voice_id(_): return ""


def find_task_result(transcript_path: str, max_attempts: int = 2) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Find task result from transcript."""
    actual_path = Path(transcript_path)

    for attempt in range(max_attempts):
        if attempt > 0:
            time.sleep(0.2)

        if not actual_path.exists():
            # Try to find most recent agent transcript
            parent_dir = actual_path.parent
            if parent_dir.exists():
                agent_files = sorted(
                    [f for f in parent_dir.glob("agent-*.jsonl")],
                    key=lambda f: f.stat().st_mtime,
                    reverse=True
                )
                if agent_files:
                    actual_path = agent_files[0]

            if not actual_path.exists():
                continue

        try:
            content = actual_path.read_text()
            lines = content.strip().split("\n")

            for i in range(len(lines) - 1, -1, -1):
                try:
                    entry = json.loads(lines[i])

                    if entry.get("type") == "assistant" and entry.get("message", {}).get("content"):
                        for content_item in entry["message"]["content"]:
                            if content_item.get("type") == "tool_use" and content_item.get("name") == "Task":
                                tool_input = content_item.get("input", {})
                                description = tool_input.get("description")
                                tool_use_id = content_item.get("id")

                                # Look for result
                                for j in range(i + 1, len(lines)):
                                    result_entry = json.loads(lines[j])
                                    if result_entry.get("type") == "user" and result_entry.get("message", {}).get("content"):
                                        for result_content in result_entry["message"]["content"]:
                                            if (result_content.get("type") == "tool_result" and
                                                result_content.get("tool_use_id") == tool_use_id):

                                                task_output = ""
                                                rc = result_content.get("content")
                                                if isinstance(rc, str):
                                                    task_output = rc
                                                elif isinstance(rc, list):
                                                    task_output = "\n".join(
                                                        item.get("text", "")
                                                        for item in rc
                                                        if item.get("type") == "text"
                                                    )

                                                agent_type = tool_input.get("subagent_type", "default")
                                                return task_output, agent_type, description

                except json.JSONDecodeError:
                    continue

        except Exception:
            continue

    return None, None, None


def extract_completion_message(task_output: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract completion message from task output."""
    # Look for COMPLETED section with agent tag
    agent_patterns = [
        r"🎯\s*COMPLETED:\s*\[AGENT:(\w+[-\w]*)\]\s*(.+?)(?:\n|$)",
        r"COMPLETED:\s*\[AGENT:(\w+[-\w]*)\]\s*(.+?)(?:\n|$)",
        r"🎯.*COMPLETED.*\[AGENT:(\w+[-\w]*)\]\s*(.+?)(?:\n|$)",
    ]

    for pattern in agent_patterns:
        match = re.search(pattern, task_output, re.IGNORECASE | re.DOTALL)
        if match and match.group(1) and match.group(2):
            agent_type = match.group(1).lower()
            message = match.group(2).strip()

            # Clean for speech
            message = clean_for_speech(message)

            # Format
            agent_name = agent_type.capitalize()

            # Don't prepend "completed" for greetings or questions
            is_greeting = re.match(r"^(hey|hello|hi|greetings)", message, re.IGNORECASE)
            is_question = "?" in message

            if is_greeting or is_question:
                full_message = message
            else:
                full_message = f"{agent_name} completed {message}"

            return full_message, agent_type

    # Fallback patterns
    generic_patterns = [
        r"🎯\s*COMPLETED:\s*(.+?)(?:\n|$)",
        r"COMPLETED:\s*(.+?)(?:\n|$)",
    ]

    for pattern in generic_patterns:
        match = re.search(pattern, task_output, re.IGNORECASE)
        if match and match.group(1):
            message = match.group(1).strip()
            message = clean_for_speech(message)

            if len(message) > 5:
                return message, None

    return None, None


def send_notification(title: str, message: str, voice_id: str) -> None:
    """Send notification to voice server."""
    if httpx is None:
        return

    server_url = os.environ.get("VOICE_SERVER_URL", "http://localhost:8888/notify")

    payload = {
        "title": title,
        "message": message,
        "voice_enabled": True,
        "voice_id": voice_id
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            client.post(server_url, json=payload)
    except Exception:
        pass


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        hook_input = json.loads(stdin_data)
        transcript_path = hook_input.get("transcript_path", "")

        if not transcript_path:
            sys.exit(0)

        # Find task result
        task_output, agent_type, _ = find_task_result(transcript_path)

        if not task_output:
            sys.exit(0)

        # Extract completion message
        completion_message, extracted_agent_type = extract_completion_message(task_output)

        if not completion_message:
            sys.exit(0)

        # Determine agent type
        final_agent_type = extracted_agent_type or agent_type or "default"

        # Get voice ID for this agent type
        voice_id = get_voice_id(final_agent_type)

        # Send voice notification
        agent_name = final_agent_type.capitalize()
        send_notification(agent_name, completion_message, voice_id)

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Subagent voice hook error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
