#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Voice notification for main agent completions.
Sends completion messages to voice server for TTS output.

Migrated from ~/.config/pai/hooks/stop-hook-voice.ts
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

try:
    from prosody_enhancer import enhance_prosody, clean_for_speech, get_voice_id
except ImportError:
    # Fallback if module not found
    def enhance_prosody(msg, _): return msg
    def clean_for_speech(msg): return msg
    def get_voice_id(_): return ""


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


def extract_completion(text: str, agent_type: str = "default") -> str:
    """Extract completion message with prosody enhancement."""
    # Remove system-reminder tags
    text = re.sub(r"<system-reminder>[\s\S]*?</system-reminder>", "", text)

    # Look for COMPLETED section
    patterns = [
        r"🎯\s*\*{0,2}COMPLETED:?\*{0,2}\s*(.+?)(?:\n|$)",
        r"\*{0,2}COMPLETED:?\*{0,2}\s*(.+?)(?:\n|$)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1):
            completed = match.group(1).strip()

            # Clean agent tags
            completed = re.sub(r"^\[AGENT:\w+\]\s*", "", completed, flags=re.IGNORECASE)

            # Clean for speech
            completed = clean_for_speech(completed)

            # Enhance with prosody
            completed = enhance_prosody(completed, agent_type)

            return completed

    return "Completed task"


def get_last_assistant_message(transcript_path: str) -> str:
    """Read last assistant message from transcript."""
    try:
        path = Path(transcript_path)
        if not path.exists():
            return ""

        content = path.read_text()
        lines = content.strip().split("\n")

        last_message = ""
        for line in lines:
            if line.strip():
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant" and entry.get("message", {}).get("content"):
                        text = content_to_text(entry["message"]["content"])
                        if text:
                            last_message = text
                except json.JSONDecodeError:
                    continue

        return last_message
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return ""


def send_notification(title: str, message: str, voice_id: str) -> None:
    """Send notification to voice server."""
    if httpx is None:
        return

    server_url = os.environ.get("VOICE_SERVER_URL", "http://localhost:8888/notify")

    payload = {
        "title": title,
        "message": message,
        "voice_enabled": True,
        "priority": "normal",
        "voice_id": voice_id
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            client.post(server_url, json=payload)
    except Exception:
        # Fail silently - voice server may not be running
        pass


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        hook_input = json.loads(stdin_data)
        transcript_path = hook_input.get("transcript_path", "")

        # Extract completion from transcript
        completion = "Completed task"
        agent_type = "default"

        if transcript_path:
            last_message = get_last_assistant_message(transcript_path)
            if last_message:
                completion = extract_completion(last_message, agent_type)

        # Get voice ID for this agent
        voice_id = get_voice_id(agent_type)

        # Send voice notification
        send_notification("Claude", completion, voice_id)

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Stop voice hook error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
