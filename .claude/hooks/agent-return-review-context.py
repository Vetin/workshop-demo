#!/usr/bin/env python3
"""
agent-return-review-context.py — PostToolUse(Agent) hook.

When an Agent tool call returns, inject the review-router output into
the assistant context so the orchestrator knows which reviewers to dispatch.

If .sdd/evidence/review-router.latest.json exists and is non-empty,
append a structured block to the tool response context.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / ".sdd" / "evidence"
ROUTER_FILE = EVIDENCE_DIR / "review-router.latest.json"


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name != "Agent":
        sys.exit(0)

    if not ROUTER_FILE.exists():
        sys.exit(0)

    try:
        router_data = json.loads(ROUTER_FILE.read_text())
    except Exception:
        sys.exit(0)

    reviewers = router_data.get("reviewers", [])
    gate_level = router_data.get("gate_level", "unknown")
    changed_files = router_data.get("changed_files", [])

    if not reviewers:
        sys.exit(0)

    # Build context injection
    reviewer_list = "\n".join(f"  • {r['agent']}: {r['reason']}" for r in reviewers)
    files_list = "\n".join(f"  - {f}" for f in changed_files[:20])

    context = f"""
---
## 🔍 Review Router Output (.sdd/evidence/review-router.latest.json)

**Gate level:** {gate_level}

**Changed files ({len(changed_files)}):**
{files_list}{"..." if len(changed_files) > 20 else ""}

**Reviewers to dispatch ({len(reviewers)}):**
{reviewer_list}

> Orchestrator: dispatch these reviewer agents now. Do not claim completion
> until all reviewers have returned findings and blockers are resolved.
---
"""

    response = {
        "decision": "allow",
        "reason": context.strip(),
    }
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
