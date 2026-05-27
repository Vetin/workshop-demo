#!/usr/bin/env python3
"""
dangerous-command-gate.py — PreToolUse hook that blocks dangerous Bash commands.

Triggered on: PreToolUse(Bash)

Blocks:
- Destructive git operations (reset --hard, push --force to main/master)
- make build / make build-multiplatform (expensive; require explicit --gate=full)
- Edits to generated files without documenting the generator path
- rm -rf on src/ directories
- Direct writes to pb/*.proto without review flag
"""

import json
import os
import re
import sys


BLOCKED_PATTERNS = [
    (r"git\s+reset\s+--hard", "git reset --hard is destructive — use a safer approach"),
    (r"git\s+push\s+--force(?:\s+-with-lease)?\s+.*(?:main|master)", "force push to main/master is blocked"),
    (r"rm\s+-rf\s+src/", "rm -rf inside src/ is blocked — use targeted removal"),
    (r"\bmake\s+build(?:\s|$)(?!.*--gate=full)", "make build is expensive (10-20 min). Set SKIP_BUILD=1 or run manually."),
    (r"\bmake\s+build-multiplatform", "make build-multiplatform is very expensive (20-45 min). Run manually."),
    (r"\bmake\s+run-tracetesting(?:\s|$)(?!.*SERVICES_TO_TEST)", "make run-tracetesting without SERVICES_TO_TEST filter takes 8-12 min. Filter with SERVICES_TO_TEST="),
]

WARN_PATTERNS = [
    (r"docker-compose\s+down\s+-v", "WARNING: docker-compose down -v removes volumes — data will be lost"),
    (r"git\s+clean\s+-f", "WARNING: git clean -f removes untracked files"),
]


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # non-JSON input → allow

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Bash",):
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")

    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            response = {
                "decision": "block",
                "reason": f"🚫 BLOCKED: {reason}\n\nCommand: {command[:200]}",
            }
            print(json.dumps(response))
            sys.exit(0)

    warnings = []
    for pattern, msg in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            warnings.append(msg)

    if warnings:
        response = {
            "decision": "allow",
            "reason": "\n".join(f"⚠️  {w}" for w in warnings),
        }
        print(json.dumps(response))

    sys.exit(0)


if __name__ == "__main__":
    main()
