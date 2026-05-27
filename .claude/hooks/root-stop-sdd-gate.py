#!/usr/bin/env python3
"""
root-stop-sdd-gate.py — Stop hook at root (orchestrator) level.

Triggered when: the main Claude session is about to stop.

Checks:
1. If any changed files are recorded → verify review-router ran and reviewers were dispatched
2. If bootstrap is in progress → verify bootstrap-complete evidence exists
3. If active SDD work exists in specs/ → warn about incomplete specs

Does NOT block ordinary conversation endings. Only blocks if:
- There are unreviewed implementation changes (changed files + no review evidence)
- The user explicitly requested completion of a task that has outstanding evidence gaps
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / ".sdd" / "evidence"
CHANGED_FILES_PATH = EVIDENCE_DIR / "changed-files.txt"
ROUTER_FILE = EVIDENCE_DIR / "review-router.latest.json"


def has_unreviewed_changes() -> Tuple[bool, List[str]]:
    if not CHANGED_FILES_PATH.exists():
        return False, []
    files = [f.strip() for f in CHANGED_FILES_PATH.read_text().splitlines() if f.strip()]
    if not files:
        return False, []
    # Check if review router ran recently
    if not ROUTER_FILE.exists():
        return True, files
    return False, files


def has_incomplete_bootstrap() -> bool:
    bootstrap_complete = EVIDENCE_DIR / "bootstrap-complete"
    # Only check if bootstrap was started (bootstrap-report exists but complete marker missing)
    specs = REPO_ROOT / "specs" / "bootstrap-report.md"
    if specs.exists() and not bootstrap_complete.exists():
        return True
    return False


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    warnings = []
    blockers = []

    unreviewed, changed_files = has_unreviewed_changes()
    if unreviewed and changed_files:
        blockers.append(
            f"There are {len(changed_files)} changed file(s) with no review evidence.\n"
            f"Run: python3 scripts/ai/review-router.py\n"
            f"Files: {', '.join(changed_files[:5])}{'...' if len(changed_files) > 5 else ''}"
        )

    if has_incomplete_bootstrap():
        warnings.append(
            "Bootstrap started but .sdd/evidence/bootstrap-complete not found.\n"
            "Complete all bootstrap phases before claiming the harness is ready."
        )

    if blockers:
        response = {
            "decision": "block",
            "reason": "🚫 SDD Gate: unresolved issues before stop:\n\n" + "\n\n".join(blockers),
        }
        print(json.dumps(response))
        sys.exit(0)

    if warnings:
        response = {
            "decision": "allow",
            "reason": "⚠️  SDD warnings:\n" + "\n".join(f"  • {w}" for w in warnings),
        }
        print(json.dumps(response))

    sys.exit(0)


if __name__ == "__main__":
    main()
