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


def find_task_result(transcript_path: str):
    path = Path(transcript_path)
    if not path.exists():
        parent_dir = path.parent
        if parent_dir.exists():
            agent_files = sorted(
                [f for f in parent_dir.glob("agent-*.jsonl")],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if agent_files:
                path = agent_files[0]

    if not path.exists():
        return None, None, None

    try:
        lines = path.read_text().strip().split("\n")
        for i in range(len(lines) - 1, -1, -1):
            try:
                entry = json.loads(lines[i])
                if entry.get("type") != "assistant":
                    continue
                for content_item in entry.get("message", {}).get("content", []):
                    if content_item.get("type") == "tool_use" and content_item.get("name") == "Task":
                        tool_input = content_item.get("input", {})
                        description = tool_input.get("description")
                        tool_use_id = content_item.get("id")
                        agent_type = tool_input.get("subagent_type", "default")

                        for j in range(i + 1, len(lines)):
                            try:
                                result_entry = json.loads(lines[j])
                            except json.JSONDecodeError:
                                continue
                            if result_entry.get("type") != "user":
                                continue
                            for rc in result_entry.get("message", {}).get("content", []):
                                if rc.get("type") == "tool_result" and rc.get("tool_use_id") == tool_use_id:
                                    content = rc.get("content")
                                    if isinstance(content, str):
                                        return content, agent_type, description
                                    elif isinstance(content, list):
                                        text = "\n".join(
                                            item.get("text", "") for item in content if item.get("type") == "text"
                                        )
                                        return text, agent_type, description
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    return None, None, None


def clean_for_speech(text: str) -> str:
    text = re.sub(r"<system-reminder>[\s\S]*?</system-reminder>", "", text)
    text = re.sub(r"```[\s\S]*?```", "code block", text)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"[\U0001F300-\U0001F9FF]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_completion(task_output: str, description: str) -> str:
    cleaned = clean_for_speech(task_output)

    for pattern in [
        r"COMPLETED:?\s*(?:\[AGENT:\w+[-\w]*\]\s*)?(.+?)(?:\n|$)",
        r"Done[.!:]\s*(.+?)(?:\n|$)",
    ]:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match and len(match.group(1).strip()) > 5:
            return match.group(1).strip()[:200]

    if description:
        return f"Finished {description}"

    sentences = re.split(r"[.!?\n]", cleaned)
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            return s[:200]

    return "Subagent complete"


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
    log_path = os.path.join(log_dir, "subagent_stop.json")

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
        completion = "Subagent complete"
        if transcript_path:
            task_output, agent_type, description = find_task_result(transcript_path)
            if task_output:
                completion = extract_completion(task_output, description)
        speak(completion)

    sys.exit(0)


if __name__ == "__main__":
    main()
