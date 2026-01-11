#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Create structured session summaries when Claude Code sessions end.
Migrated and enhanced from ~/.config/pai/hooks/capture-session-summary.ts

Outputs JSON format per the learnings system specification.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set


def get_local_timestamp() -> str:
    """Get formatted local timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_iso_timestamp() -> str:
    """Get ISO format timestamp."""
    return datetime.now().isoformat() + "Z"


def determine_session_focus(files_changed: List[str], commands_executed: List[str]) -> str:
    """Determine the primary focus of the session based on activity."""
    file_patterns = [f.lower() for f in files_changed]

    if any('/blog/' in f or '/posts/' in f for f in file_patterns):
        return 'blog-work'
    if any('/hooks/' in f for f in file_patterns):
        return 'hook-development'
    if any('/skills/' in f for f in file_patterns):
        return 'skill-updates'
    if any('/agents/' in f for f in file_patterns):
        return 'agent-work'
    if any('/learnings/' in f for f in file_patterns):
        return 'learnings-work'
    if any('test' in cmd for cmd in commands_executed):
        return 'testing-session'
    if any('git commit' in cmd for cmd in commands_executed):
        return 'git-operations'
    if any('deploy' in cmd for cmd in commands_executed):
        return 'deployment'

    if files_changed:
        main_file = Path(files_changed[0]).stem
        if main_file:
            return f'{main_file}-work'

    return 'development-session'


def analyze_session(session_id: str, year_month: str) -> Dict[str, Any]:
    """Analyze session activity from raw event logs."""
    claude_dir = Path.home() / ".claude"
    raw_outputs_dir = claude_dir / "history" / "raw-outputs" / year_month

    files_changed: Set[str] = set()
    commands_executed: List[str] = []
    tools_used: Set[str] = set()
    key_decisions: List[Dict[str, str]] = []

    try:
        if raw_outputs_dir.exists():
            for jsonl_file in raw_outputs_dir.glob("*.jsonl"):
                content = jsonl_file.read_text()
                for line in content.strip().split('\n'):
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        payload = entry.get("payload", {})

                        # Only process events from this session
                        if payload.get("session_id") != session_id:
                            continue

                        tool_name = payload.get("tool_name", "")
                        tool_input = payload.get("tool_input", {})

                        if tool_name:
                            tools_used.add(tool_name)

                        if tool_name in ("Edit", "Write"):
                            file_path = tool_input.get("file_path", "")
                            if file_path:
                                files_changed.add(file_path)

                        if tool_name == "Bash":
                            command = tool_input.get("command", "")
                            if command:
                                commands_executed.append(command)

                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass

    files_list = list(files_changed)[:10]
    commands_list = commands_executed[:10]

    return {
        "focus": determine_session_focus(files_list, commands_list),
        "files_changed": [{"path": f, "operation": "modified"} for f in files_list],
        "commands_executed": commands_list,
        "tools_used": list(tools_used),
        "key_decisions": key_decisions
    }


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        data = json.loads(stdin_data)
        claude_dir = Path.home() / ".claude"
        history_dir = claude_dir / "history"

        now = datetime.now()
        timestamp = now.strftime("%Y%m%dT%H%M%S")
        year_month = now.strftime("%Y-%m")

        session_id = data.get("session_id", data.get("conversation_id", "unknown"))
        transcript_path = data.get("transcript_path", "")

        session_info = analyze_session(session_id, year_month)
        filename = f"{timestamp}_{session_id[:8]}_{session_info['focus']}.json"

        session_dir = history_dir / "sessions" / year_month
        session_dir.mkdir(parents=True, exist_ok=True)

        # Build structured session log per plan specification
        session_log = {
            "version": "1.0",
            "session_id": session_id,
            "title": f"Session: {session_info['focus'].replace('-', ' ').title()}",
            "started_at": None,  # Would need to track from SessionStart
            "ended_at": get_iso_timestamp(),
            "summary": f"Development session focused on {session_info['focus'].replace('-', ' ')}",
            "key_decisions": session_info["key_decisions"],
            "files_changed": session_info["files_changed"],
            "commands_executed": session_info["commands_executed"],
            "tools_used": session_info["tools_used"],
            "potential_learnings": [],  # Populated by stop_learnings.py
            "transcript_path": transcript_path
        }

        # Write JSON session log
        output_path = session_dir / filename
        output_path.write_text(json.dumps(session_log, indent=2))

        print(f"Session summary saved to sessions/{year_month}/{filename}")

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Session summary error: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
