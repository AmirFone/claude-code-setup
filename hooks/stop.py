#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from local_tts import speak


def extract_last_assistant_text(transcript_path: str) -> str:
    path = Path(transcript_path)
    if not path.exists():
        return ""

    try:
        lines = path.read_text().strip().split("\n")
        last_text = ""
        for line in lines:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if entry.get("type") != "assistant":
                    continue
                content = entry.get("message", {}).get("content")
                if isinstance(content, str) and content.strip():
                    last_text = content.strip()
                elif isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, str):
                            parts.append(c)
                        elif isinstance(c, dict) and c.get("text"):
                            parts.append(c["text"])
                    text = " ".join(parts).strip()
                    if text:
                        last_text = text
            except json.JSONDecodeError:
                continue
        return last_text
    except Exception:
        return ""


def clean_for_speech(text: str) -> str:
    text = re.sub(r"<system-reminder>[\s\S]*?</system-reminder>", "", text)
    text = re.sub(r"```[\s\S]*?```", "code block", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[\U0001F300-\U0001F9FF]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_completion_summary(text: str) -> str:
    text = clean_for_speech(text)

    # Look for explicit COMPLETED markers
    for pattern in [
        r"COMPLETED:?\s*(.+?)(?:\n|$)",
        r"Done[.!:]\s*(.+?)(?:\n|$)",
    ]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and len(match.group(1).strip()) > 5:
            summary = match.group(1).strip()
            return summary[:200]

    # Take first meaningful sentence
    sentences = re.split(r"[.!?\n]", text)
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            return s[:200]

    return "Task complete"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat", action="store_true")
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "stop.json")

    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                log_data = json.load(f)
        else:
            log_data = []
    except (json.JSONDecodeError, ValueError):
        log_data = []

    log_data.append(input_data)
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    if args.chat and "transcript_path" in input_data:
        transcript_path = input_data["transcript_path"]
        if os.path.exists(transcript_path):
            try:
                chat_data = []
                with open(transcript_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                chat_data.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                chat_file = os.path.join(log_dir, "chat.json")
                with open(chat_file, "w") as f:
                    json.dump(chat_data, f, indent=2)
            except Exception:
                pass

    if args.notify:
        transcript_path = input_data.get("transcript_path", "")
        completion = "Task complete"
        if transcript_path:
            last_message = extract_last_assistant_text(transcript_path)
            if last_message:
                completion = extract_completion_summary(last_message)
        speak(completion)

    sys.exit(0)


if __name__ == "__main__":
    main()
