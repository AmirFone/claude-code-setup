#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
import json
import os
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from local_tts import speak


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        sys.exit(0)

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "notification.json")

    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                log_data = json.load(f)
        else:
            log_data = []
    except (json.JSONDecodeError, ValueError):
        log_data = []

    log_data.append(input_data)
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    if args.notify and input_data.get("message") != "Claude is waiting for your input":
        engineer_name = os.getenv("ENGINEER_NAME", "").strip()
        if engineer_name and random.random() < 0.3:
            message = f"{engineer_name}, your agent needs your input"
        else:
            message = "Your agent needs your input"
        speak(message)

    sys.exit(0)


if __name__ == "__main__":
    main()
