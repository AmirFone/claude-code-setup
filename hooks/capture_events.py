#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Capture all Claude Code hook events to JSONL files.
Migrated from ~/.config/pai/hooks/capture-all-events.ts
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path


def get_local_timestamp() -> str:
    """Get formatted local timestamp."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_events_file_path() -> Path:
    """Get path for today's events JSONL file."""
    claude_dir = Path.home() / ".claude"
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    date_str = now.strftime("%Y-%m-%d")

    month_dir = claude_dir / "history" / "raw-outputs" / year_month
    month_dir.mkdir(parents=True, exist_ok=True)

    return month_dir / f"{date_str}_all-events.jsonl"


def get_session_mapping_file() -> Path:
    """Get path for agent-session mapping file."""
    return Path.home() / ".claude" / "agent-sessions.json"


def get_agent_for_session(session_id: str) -> str:
    """Get the agent name for a session."""
    try:
        mapping_file = get_session_mapping_file()
        if mapping_file.exists():
            mappings = json.loads(mapping_file.read_text())
            return mappings.get(session_id, os.environ.get("DA", "main"))
    except Exception:
        pass
    return os.environ.get("DA", "main")


def set_agent_for_session(session_id: str, agent_name: str) -> None:
    """Set the agent name for a session."""
    try:
        mapping_file = get_session_mapping_file()
        mappings = {}

        if mapping_file.exists():
            mappings = json.loads(mapping_file.read_text())

        mappings[session_id] = agent_name
        mapping_file.write_text(json.dumps(mappings, indent=2))
    except Exception:
        pass


def extract_agent_metadata(tool_input: dict, description: str = None) -> dict:
    """Extract agent instance metadata from Task tool calls."""
    result = {}

    # Strategy 1: Extract from description [agent-type-N]
    if description:
        match = re.search(r'\[([a-z-]+-researcher)-(\d+)\]', description)
        if match:
            result["agent_type"] = match.group(1)
            result["instance_number"] = int(match.group(2))
            result["agent_instance_id"] = f"{result['agent_type']}-{result['instance_number']}"

    # Strategy 2: Extract from prompt [AGENT_INSTANCE: ...]
    prompt = tool_input.get("prompt", "") if tool_input else ""
    if not result.get("agent_instance_id") and prompt:
        match = re.search(r'\[AGENT_INSTANCE:\s*([^\]]+)\]', prompt)
        if match:
            result["agent_instance_id"] = match.group(1).strip()
            parts = re.match(r'^([a-z-]+)-(\d+)$', result["agent_instance_id"])
            if parts:
                result["agent_type"] = parts.group(1)
                result["instance_number"] = int(parts.group(2))

    # Strategy 3: Extract parent session from prompt
    if prompt:
        parent_match = re.search(r'\[PARENT_SESSION:\s*([^\]]+)\]', prompt)
        if parent_match:
            result["parent_session_id"] = parent_match.group(1).strip()

        task_match = re.search(r'\[PARENT_TASK:\s*([^\]]+)\]', prompt)
        if task_match:
            result["parent_task_id"] = task_match.group(1).strip()

    # Strategy 4: Fallback to subagent_type
    if not result.get("agent_type") and tool_input and tool_input.get("subagent_type"):
        result["agent_type"] = tool_input["subagent_type"]

    return result


def is_agent_spawning_call(tool_name: str, tool_input: dict) -> bool:
    """Check if a tool call is spawning a subagent."""
    return tool_name == "Task" and tool_input and "subagent_type" in tool_input


def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--event-type", required=True, help="Type of hook event")
        args = parser.parse_args()

        event_type = args.event_type

        # Read JSON input from stdin
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        hook_data = json.loads(stdin_data)

        session_id = hook_data.get("session_id", "main")
        agent_name = get_agent_for_session(session_id)

        # Update agent mapping based on event type
        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        if tool_name == "Task" and tool_input.get("subagent_type"):
            agent_name = tool_input["subagent_type"]
            set_agent_for_session(session_id, agent_name)
        elif event_type in ("SubagentStop", "Stop"):
            agent_name = os.environ.get("DA", "main")
            set_agent_for_session(session_id, agent_name)
        elif os.environ.get("CLAUDE_CODE_AGENT"):
            agent_name = os.environ["CLAUDE_CODE_AGENT"]
            set_agent_for_session(session_id, agent_name)
        elif hook_data.get("agent_type"):
            agent_name = hook_data["agent_type"]
            set_agent_for_session(session_id, agent_name)

        # Build event
        event = {
            "source_app": agent_name,
            "session_id": session_id,
            "hook_event_type": event_type,
            "payload": hook_data,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "timestamp_local": get_local_timestamp()
        }

        # Enrich with agent metadata for Task calls
        if is_agent_spawning_call(tool_name, tool_input):
            description = hook_data.get("description", "")
            metadata = extract_agent_metadata(tool_input, description)
            event.update(metadata)

        # Append to events file
        events_file = get_events_file_path()
        with open(events_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Event capture error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
