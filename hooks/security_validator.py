#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Security validator for Bash commands.
Validates commands and blocks dangerous operations.

Migrated from ~/.config/pai/hooks/security-validator.ts

Exit codes:
- 0: Allow the command
- 2: Block the command (Claude Code will see the message)
"""

import json
import re
import sys
from typing import Dict, List, Tuple, Any


# Attack pattern categories with their patterns, actions, and messages
ATTACK_PATTERNS: Dict[str, Dict[str, Any]] = {
    # Tier 1: Catastrophic - Always block
    "catastrophic": {
        "patterns": [
            r"rm\s+(-rf?|--recursive)\s+[\/~]",     # rm -rf /
            r"rm\s+(-rf?|--recursive)\s+\*",         # rm -rf *
            r">\s*\/dev\/sd[a-z]",                   # Overwrite disk
            r"mkfs\.",                               # Format filesystem
            r"dd\s+if=.*of=\/dev",                   # dd to device
        ],
        "action": "block",
        "message": "BLOCKED: Catastrophic deletion/destruction detected"
    },

    # Tier 2: Reverse shells - Always block
    "reverse_shell": {
        "patterns": [
            r"bash\s+-i\s+>&\s*\/dev\/tcp",         # Bash reverse shell
            r"nc\s+(-e|--exec)\s+\/bin\/(ba)?sh",   # Netcat shell
            r"python.*socket.*connect",              # Python socket
            r"perl.*socket.*connect",                # Perl socket
            r"ruby.*TCPSocket",                      # Ruby socket
            r"php.*fsockopen",                       # PHP socket
            r"socat.*exec",                          # Socat exec
            r"\|\s*\/bin\/(ba)?sh",                 # Pipe to shell
        ],
        "action": "block",
        "message": "BLOCKED: Reverse shell pattern detected"
    },

    # Tier 3: Credential theft - Always block
    "credential_theft": {
        "patterns": [
            r"curl.*\|\s*(ba)?sh",                  # curl pipe to shell
            r"wget.*\|\s*(ba)?sh",                  # wget pipe to shell
            r"curl.*(-o|--output).*&&.*chmod.*\+x", # Download and execute
            r"base64\s+-d.*\|\s*(ba)?sh",           # Base64 decode to shell
        ],
        "action": "block",
        "message": "BLOCKED: Remote code execution pattern detected"
    },

    # Tier 4: Prompt injection indicators - Block and log
    "prompt_injection": {
        "patterns": [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?prior\s+instructions",
            r"you\s+are\s+now\s+(in\s+)?[a-z]+\s+mode",
            r"new\s+instruction[s]?:",
            r"system\s+prompt:",
            r"\[INST\]",                             # LLM injection
            r"<\|im_start\|>",                       # ChatML injection
        ],
        "action": "block",
        "message": "BLOCKED: Prompt injection pattern detected - logging incident"
    },

    # Tier 5: Environment manipulation - Warn
    "env_manipulation": {
        "patterns": [
            r"export\s+(ANTHROPIC|OPENAI|AWS|AZURE)_",  # API key export
            r"echo\s+\$\{?(ANTHROPIC|OPENAI)_",         # Echo API keys
            r"env\s*\|.*KEY",                            # Dump env with keys
            r"printenv.*KEY",                            # Print env keys
        ],
        "action": "warn",
        "message": "WARNING: Environment/credential access detected"
    },

    # Tier 6: Git dangerous operations - Require confirmation
    "git_dangerous": {
        "patterns": [
            r"git\s+push.*(-f|--force)",            # Force push
            r"git\s+reset\s+--hard",                # Hard reset
            r"git\s+clean\s+-fd",                   # Clean untracked
            r"git\s+checkout\s+--\s+\.",            # Discard all changes
        ],
        "action": "confirm",
        "message": "CONFIRM: Potentially destructive git operation"
    },

    # Tier 7: System modification - Log
    "system_mod": {
        "patterns": [
            r"chmod\s+777",                         # World writable
            r"chown\s+root",                        # Change to root
            r"sudo\s+",                             # Sudo usage
            r"systemctl\s+(stop|disable)",          # Stop services
        ],
        "action": "log",
        "message": "LOGGED: System modification command"
    },

    # Tier 8: Network operations - Log
    "network": {
        "patterns": [
            r"ssh\s+",                              # SSH connections
            r"scp\s+",                              # SCP transfers
            r"rsync.*:",                            # Rsync remote
            r"curl\s+(-X\s+POST|--data)",          # POST requests
        ],
        "action": "log",
        "message": "LOGGED: Network operation"
    },

    # Tier 9: Data exfiltration patterns - Block
    "exfiltration": {
        "patterns": [
            r"curl.*(@|--upload-file)",             # Upload file
            r"tar.*\|.*curl",                       # Tar and send
            r"zip.*\|.*nc",                         # Zip and netcat
        ],
        "action": "block",
        "message": "BLOCKED: Data exfiltration pattern detected"
    },

    # Tier 10: Claude infrastructure protection - Block
    "claude_protection": {
        "patterns": [
            r"rm.*\.claude",                        # Delete Claude config
            r"rm\s+-rf?\s+~\/\.claude",            # Delete Claude dir
            r"git\s+push.*\.claude.*public",       # Push secrets to public
        ],
        "action": "block",
        "message": "BLOCKED: Claude infrastructure protection triggered"
    }
}


def validate_command(command: str) -> Tuple[bool, str, str]:
    """
    Validate a command against attack patterns.

    Returns:
        Tuple of (allowed: bool, message: str, action: str)
    """
    # Fast path: Most commands are safe
    if not command or len(command) < 3:
        return (True, "", "")

    # Check each tier
    for tier_name, tier in ATTACK_PATTERNS.items():
        for pattern in tier["patterns"]:
            if re.search(pattern, command, re.IGNORECASE):
                action = tier["action"]
                message = tier["message"]

                # Log security event
                print(f"[Security] {tier_name}: {message}", file=sys.stderr)
                print(f"[Security] Command: {command[:100]}...", file=sys.stderr)

                return (action != "block", message, action)

    return (True, "", "")


def main():
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            sys.exit(0)

        payload = json.loads(stdin_data)

        # Only validate Bash commands
        if payload.get("tool_name") != "Bash":
            sys.exit(0)

        command = payload.get("tool_input", {}).get("command", "")
        if not command:
            sys.exit(0)

        allowed, message, action = validate_command(command)

        if not allowed:
            # Output the block message - Claude Code will see this
            print(message)
            print(f"Command blocked: {command[:100]}...")

            # Exit with code 2 to signal block (Claude Code specific)
            sys.exit(2)

        # Log warnings but allow execution
        if action in ("warn", "confirm"):
            print(message)

    except json.JSONDecodeError:
        pass
    except Exception as e:
        # Never crash - log error and allow command
        print(f"Security validator error: {e}", file=sys.stderr)

    # Exit 0 = allow the command
    sys.exit(0)


if __name__ == "__main__":
    main()
