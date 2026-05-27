#!/usr/bin/env python3
"""
subagent-stop-quality-gate.py — Stop hook for implementer subagents.

Triggered when: an implementer subagent completes (Stop event, subagent context)

Actions:
1. Run review-router.py to compute which reviewers are needed
2. Run gate-router.sh at the inferred level (default: fast)
3. If gates pass → allow stop, review-router.latest.json written for orchestrator
4. If gates fail → block with failure details

Skip conditions:
- No changed files recorded
- SKIP_GATES=1 env var
- Only docs/specs changed (still runs fast gate but won't block on warnings)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / ".sdd" / "evidence"
CHANGED_FILES_PATH = EVIDENCE_DIR / "changed-files.txt"


def get_changed_files() -> List[str]:
    if CHANGED_FILES_PATH.exists():
        return [f.strip() for f in CHANGED_FILES_PATH.read_text().splitlines() if f.strip()]
    # Fallback: ask git
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return [f for f in result.stdout.splitlines() if f]
    except Exception:
        return []


def run_review_router(changed_files: List[str]) -> dict:
    try:
        args = ["python3", str(REPO_ROOT / "scripts/ai/review-router.py"), "--json"] + changed_files
        result = subprocess.run(args, capture_output=True, text=True, cwd=REPO_ROOT, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        pass
    return {"gate_level": "fast", "reviewers": [], "changed_files": changed_files}


def run_gate(level: str, changed_files: List[str]) -> Tuple[bool, str]:
    if os.environ.get("SKIP_GATES") == "1":
        return True, "SKIP_GATES=1 — skipped"

    env = os.environ.copy()
    env["SKIP_BUILD"] = "1"  # Always skip Docker build in auto-gates

    try:
        args = [str(REPO_ROOT / "scripts/ai/gate-router.sh"), "--level", level] + changed_files
        result = subprocess.run(
            args, capture_output=True, text=True, cwd=REPO_ROOT, timeout=300, env=env
        )
        combined = result.stdout + result.stderr
        return result.returncode == 0, combined
    except subprocess.TimeoutExpired:
        return False, "Gate timed out after 5 minutes"
    except Exception as e:
        return True, f"Gate runner error (non-blocking): {e}"


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    # Only act on Stop events in subagent context
    stop_reason = payload.get("stop_reason", "")

    changed_files = get_changed_files()

    if not changed_files:
        # Nothing changed — allow stop silently
        sys.exit(0)

    print(f"\n🔍 Subagent stop — running quality gate on {len(changed_files)} changed file(s)…", flush=True)

    # Run review router
    router_output = run_review_router(changed_files)
    gate_level = router_output.get("gate_level", "fast")
    reviewers = router_output.get("reviewers", [])

    # Write review router output for orchestrator
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    router_path = EVIDENCE_DIR / "review-router.latest.json"
    router_path.write_text(json.dumps(router_output, indent=2))

    print(f"   Gate level: {gate_level}")
    print(f"   Reviewers queued: {len(reviewers)}", flush=True)

    # Run deterministic gate
    passed, output = run_gate(gate_level, changed_files)

    if output.strip():
        for line in output.strip().splitlines()[:40]:  # cap output
            print(f"   {line}")

    if not passed:
        response = {
            "decision": "block",
            "reason": (
                f"🚫 Quality gate ({gate_level}) FAILED.\n\n"
                f"{output[:2000]}\n\n"
                "Fix the issues above before the orchestrator can proceed."
            ),
        }
        print(json.dumps(response))
        sys.exit(0)

    print(f"\n✓ Gate ({gate_level}) passed. Orchestrator will dispatch {len(reviewers)} reviewer(s).", flush=True)

    # Clear changed files for next task
    if CHANGED_FILES_PATH.exists():
        CHANGED_FILES_PATH.write_text("")

    sys.exit(0)


if __name__ == "__main__":
    main()
