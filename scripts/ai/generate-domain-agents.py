#!/usr/bin/env python3
"""
generate-domain-agents.py

Reference implementation: generates one domain expert agent file per service
defined in docs/ai-knowledge/services/service-inventory.json.

Run from repo root:
    python scripts/ai/generate-domain-agents.py
    python scripts/ai/generate-domain-agents.py --force   # overwrite existing files
"""

import json
import os
import pathlib
import argparse
import sys

# ---------------------------------------------------------------------------
# Paths (all relative to repo root, resolved at runtime)
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "docs/ai-knowledge/services/service-inventory.json"
AGENTS_DIR = REPO_ROOT / ".claude/agents"


def sanitize_port(port) -> str:
    """Return a human-readable port string."""
    return str(port) if port is not None else "none (no HTTP port exposed)"


def build_description(service: dict) -> str:
    """One-line frontmatter description for the agent."""
    name = service["name"].title()
    lang = service["language"]
    framework = service["framework"]
    return (
        f"Read-only domain expert for the {name} service "
        f"({lang}/{framework}). Consult for architecture questions, "
        f"dependency boundaries, and OTel instrumentation patterns for this service."
    )


def build_otel_summary(otel: str) -> str:
    """
    The otel_instrumentation strings in the inventory are fairly long.
    Shorten them slightly for the agent body while keeping them readable.
    The full text is preserved; we only strip redundant trailing phrases
    like '(manual)' when they duplicate earlier words.
    """
    return otel.strip()


def render_agent(service: dict) -> str:
    """Return the full Markdown content for a domain expert agent."""
    name = service["name"]
    title = name.title()
    lang = service["language"]
    framework = service["framework"]
    port = sanitize_port(service.get("port"))
    dockerfile = service.get("dockerfile") or "none"
    entrypoint = service.get("entrypoint") or "none"
    deps = service.get("dependencies") or []
    deps_str = ", ".join(deps) if deps else "none"
    comm = service.get("communication_type") or []
    comm_str = ", ".join(comm) if comm else "none"
    otel = build_otel_summary(service.get("otel_instrumentation", ""))
    slug = name  # already kebab-case in inventory

    description = build_description(service)

    # Build knowledge-sources list. Always include the service-specific doc
    # (it may not exist yet for newly added services, but the path is canonical).
    knowledge_sources = [
        f"docs/ai-knowledge/services/{slug}.md",
        "docs/ai-knowledge/communication/overview.md",
        "docs/ai-knowledge/observability/overview.md",
    ]
    sources_md = "\n".join(f"- {s}" for s in knowledge_sources)

    return f"""\
---
name: domain-{slug}-expert
description: {description}
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are the domain expert for the {title} service in the OpenTelemetry Demo.

## Service facts
- Language: {lang}
- Framework: {framework}
- Port: {port}
- Dockerfile: {dockerfile}
- Entry point: {entrypoint}
- Dependencies: {deps_str}
- Communication: {comm_str}
- OTel instrumentation: {otel}

## Knowledge sources
{sources_md}

## Rules
- Do not edit any files.
- Answer only from docs and source code evidence.
- Cite exact file paths when describing behavior.
- Flag any uncertainty rather than guessing.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate domain expert agent files from service-inventory.json"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing agent files",
    )
    args = parser.parse_args()

    # Validate inventory exists
    if not INVENTORY_PATH.exists():
        print(f"ERROR: inventory not found at {INVENTORY_PATH}", file=sys.stderr)
        sys.exit(1)

    with INVENTORY_PATH.open() as f:
        services = json.load(f)

    # Ensure agents directory exists
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0

    for service in services:
        slug = service["name"]
        out_path = AGENTS_DIR / f"domain-{slug}-expert.md"

        if out_path.exists() and not args.force:
            print(f"  skip  {out_path.relative_to(REPO_ROOT)}  (exists; use --force to overwrite)")
            skipped += 1
            continue

        content = render_agent(service)
        out_path.write_text(content, encoding="utf-8")
        action = "overwrite" if out_path.exists() else "create"
        print(f"  {action:8s}  {out_path.relative_to(REPO_ROOT)}")
        generated += 1

    print(f"\nDone. Generated: {generated}  Skipped: {skipped}")


if __name__ == "__main__":
    main()
