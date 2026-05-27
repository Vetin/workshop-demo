#!/usr/bin/env python3
"""
review-router.py — Determine which reviewer agents to dispatch after implementation.

Reads the list of changed files (from args or git) and writes
.sdd/evidence/review-router.latest.json with a prioritized list of reviewers.

Usage:
    python scripts/ai/review-router.py [file1 file2 ...]
    python scripts/ai/review-router.py --json   # emit JSON to stdout only

Output file: .sdd/evidence/review-router.latest.json
{
  "changed_files": [...],
  "reviewers": [
    {"agent": "technical-go-reviewer", "reason": "Go source files changed"},
    ...
  ],
  "gate_level": "fast|medium|full"
}
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / ".sdd" / "evidence"

# ── Service → language mapping ────────────────────────────────────────────────

SERVICE_LANG = {
    "accounting": "csharp",
    "cart": "csharp",
    "ad": "java",
    "kafka": "java",
    "fraud-detection": "kotlin",
    "checkout": "go",
    "product-catalog": "go",
    "currency": "cpp",
    "email": "ruby",
    "frontend": "typescript",
    "load-generator": "python",
    "product-reviews": "python",
    "recommendation": "python",
    "llm": "python",
    "payment": "javascript",
    "shipping": "rust",
    "quote": "php",
    "flagd-ui": "elixir",
}

ALWAYS_INCLUDE = [
    "docs-consistency-reviewer",
    "test-verification-reviewer",
]

CROSS_CUTTING_TRIGGERS = {
    "observability-reviewer": [
        lambda f: any(x in f for x in ["otelcol-config", "otel", "telemetry", "instrumentation", "FrontendTracer"]),
        lambda f: f.endswith(".proto"),
    ],
    "service-contract-reviewer": [
        lambda f: f.endswith(".proto"),
        lambda f: "genproto" in f,
        lambda f: "demo_pb2" in f,
        lambda f: "demo.ts" in f and "protos" in f,
    ],
    "security-data-leak-reviewer": [
        lambda f: any(x in f for x in ["payment", "checkout", "cart"]),
        lambda f: "product-reviews" in f,
    ],
    "frontend-ui-kit-reviewer": [
        lambda f: "src/frontend" in f,
    ],
}


def get_changed_files(args: List[str]) -> List[str]:
    if args:
        return args
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        files = set(result.stdout.splitlines() + staged.stdout.splitlines())
        return sorted(f for f in files if f)
    except Exception:
        return []


def service_from_path(path: str) -> Optional[str]:
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "src":
        return parts[1]
    return None


def infer_gate_level(changed_files: List[str]) -> str:
    for f in changed_files:
        if f.endswith(".proto"):
            return "medium"
        if f.startswith("src/") and not f.startswith("src/otel-collector"):
            return "medium"
        if "docker-compose" in f or f.startswith("kubernetes/") or f.startswith(".env"):
            return "medium"
    return "fast"


def compute_reviewers(changed_files: List[str]) -> List[dict]:
    reviewers = []
    seen = set()

    def add(agent: str, reason: str):
        if agent not in seen:
            reviewers.append({"agent": agent, "reason": reason})
            seen.add(agent)

    # Always include
    for r in ALWAYS_INCLUDE:
        add(r, "always included")

    # Language-specific reviewers
    touched_langs = set()
    for f in changed_files:
        svc = service_from_path(f)
        if svc and svc in SERVICE_LANG:
            touched_langs.add(SERVICE_LANG[svc])

    lang_reviewer_map = {
        "csharp":     "technical-csharp-reviewer",
        "go":         "technical-go-reviewer",
        "java":       "technical-java-reviewer",
        "kotlin":     "technical-kotlin-reviewer",
        "python":     "technical-python-reviewer",
        "typescript": "technical-typescript-reviewer",
        "ruby":       "technical-ruby-reviewer",
        "rust":       "technical-rust-reviewer",
        "php":        "technical-php-reviewer",
        "elixir":     "technical-elixir-reviewer",
        "javascript": "technical-javascript-reviewer",
        "cpp":        "technical-cpp-reviewer",
    }
    for lang in sorted(touched_langs):
        reviewer = lang_reviewer_map.get(lang)
        if reviewer:
            add(reviewer, f"{lang} source files changed")

    # Cross-cutting reviewers
    for reviewer, predicates in CROSS_CUTTING_TRIGGERS.items():
        for f in changed_files:
            if any(pred(f) for pred in predicates):
                add(reviewer, f"triggered by {f}")
                break

    # Infrastructure changes always need observability review
    for f in changed_files:
        if "otel-collector" in f or "otelcol-config" in f:
            add("observability-reviewer", "otel-collector config changed")
            break

    # Domain expert hints (for context, not blocking)
    for f in changed_files:
        svc = service_from_path(f)
        if svc:
            add(f"domain-{svc}-expert", f"touched service: {svc}")

    return reviewers


def main():
    emit_json_only = "--json" in sys.argv
    file_args = [a for a in sys.argv[1:] if not a.startswith("--")]

    changed_files = get_changed_files(file_args)
    gate_level = infer_gate_level(changed_files)
    reviewers = compute_reviewers(changed_files)

    output = {
        "changed_files": changed_files,
        "gate_level": gate_level,
        "reviewers": reviewers,
    }

    if emit_json_only:
        print(json.dumps(output, indent=2))
        return

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EVIDENCE_DIR / "review-router.latest.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"Review router output → {out_path}")
    print(f"Gate level: {gate_level}")
    print(f"Reviewers ({len(reviewers)}):")
    for r in reviewers:
        print(f"  • {r['agent']}: {r['reason']}")


if __name__ == "__main__":
    main()
