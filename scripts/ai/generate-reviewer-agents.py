#!/usr/bin/env python3
"""
generate-reviewer-agents.py

Reference implementation: generates reviewer agent files for the
OpenTelemetry Demo project.

Two categories are produced:

1. Language reviewers — one per unique language found in service-inventory.json
   (excludes N/A infrastructure services).
   Filename: .claude/agents/technical-{lang-slug}-reviewer.md

2. Cross-cutting reviewers — fixed set covering concerns that span all services.
   Filename: .claude/agents/{name}.md  (names listed in CROSS_CUTTING_REVIEWERS below)

This script READS existing agent files rather than overwriting them; it only
creates files that don't yet exist (unless --force is given).

Run from repo root:
    python scripts/ai/generate-reviewer-agents.py
    python scripts/ai/generate-reviewer-agents.py --force
"""

import json
import pathlib
import argparse
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "docs/ai-knowledge/services/service-inventory.json"
AGENTS_DIR = REPO_ROOT / ".claude/agents"

# ---------------------------------------------------------------------------
# Language → slug used in reviewer file names
# (mirrors the convention in generate-implementer-agents.py)
# ---------------------------------------------------------------------------
LANGUAGE_TO_SLUG: dict[str, str] = {
    "C#": "csharp-dotnet",
    "Go": "go",
    "Java": "java",
    "Kotlin": "kotlin",
    "Python": "python",
    "TypeScript": "typescript",
    "Ruby": "ruby",
    "Rust": "rust",
    "PHP": "php",
    "Elixir": "elixir",
    "JavaScript": "javascript-node",
    "C++": "cpp",
    # N/A is intentionally excluded from language reviewers
}

# ---------------------------------------------------------------------------
# Cross-cutting reviewer definitions
# Each entry: (filename-slug, agent-name, description, body)
# ---------------------------------------------------------------------------
CROSS_CUTTING_REVIEWERS: list[tuple[str, str, str, str]] = [
    (
        "service-contract-reviewer",
        "service-contract-reviewer",
        "Reviews changes to service contracts (proto files, API shapes, Kafka topic schemas) "
        "to ensure backward compatibility and correct inter-service wiring.",
        """\
You review changes that affect service contracts in the OpenTelemetry Demo.

## Scope

- Protobuf definitions under `src/` (`.proto` files)
- gRPC service interfaces and generated code
- Kafka topic names and message schemas
- REST/HTTP API shapes (request/response bodies, status codes)
- Feature-flag names and their expected behavior contracts

## Review checklist

1. **Backward compatibility** — does the change break any existing caller?
2. **Proto consistency** — are generated files in sync with the `.proto` source?
3. **Kafka schema** — are producers and consumers using the same message format?
4. **Dependency graph** — which services are affected by this contract change?
   (Reference: `docs/ai-knowledge/services/service-inventory.json`)
5. **Documentation** — is `docs/ai-knowledge/communication/overview.md` updated?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- affected services (list)
- findings by severity (critical / warning / info)
- exact file paths and line numbers
- required fixes for anything non-passing
""",
    ),
    (
        "observability-reviewer",
        "observability-reviewer",
        "Reviews changes for OTel instrumentation correctness: span naming, attribute "
        "conventions, metric names, log correlation, and exporter configuration.",
        """\
You review changes for OpenTelemetry instrumentation correctness.

## Knowledge sources

- `docs/ai-knowledge/observability/overview.md`
- `docs/ai-knowledge/services/service-inventory.json` (per-service instrumentation field)
- OTel semantic conventions: https://opentelemetry.io/docs/specs/semconv/

## Review checklist

1. **Span naming** — follows `<verb> <noun>` or `<system>.<operation>` convention?
2. **Attribute names** — use OTel semantic convention keys where applicable?
3. **Metrics** — counter/histogram/gauge types used correctly? Unit suffixes present?
4. **Log correlation** — trace context propagated to logs (TraceId, SpanId)?
5. **Exporter config** — OTLP endpoint / protocol unchanged? Not hardcoded?
6. **Auto-instrumentation** — bootstrap scripts (`instrument.sh`, `JAVA_TOOL_OPTIONS`,
   `opentelemetry-instrument`) not removed or bypassed?
7. **Collector pipeline** — if `otelcol-config.yml` is changed, are downstream
   exporters (Jaeger, Prometheus, OpenSearch) still receiving their expected signals?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths
- required fixes
""",
    ),
    (
        "frontend-ui-kit-reviewer",
        "frontend-ui-kit-reviewer",
        "Reviews frontend (Next.js/React) changes for UI kit consistency, "
        "component reuse, and accessibility.",
        """\
You review frontend changes in `src/frontend/` for UI consistency and quality.

## Knowledge sources

- `docs/ai-knowledge/frontend/overview.md`
- `docs/ai-knowledge/frontend/ui-kit.md` (if present)
- Existing components under `src/frontend/components/`

## Review checklist

1. **Component reuse** — does the change introduce duplicate UI patterns
   that should use an existing component?
2. **Styling** — follows the project's CSS/Tailwind/styled-components convention?
3. **Accessibility** — semantic HTML, ARIA labels, keyboard navigation?
4. **TypeScript types** — no `any` without justification; props typed correctly?
5. **OTel browser instrumentation** — trace context not stripped from fetch/XHR calls?
6. **SSR vs CSR** — is the page correctly using `getServerSideProps` / `getStaticProps`
   vs client-side hooks?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths
- required fixes
""",
    ),
    (
        "security-data-leak-reviewer",
        "security-data-leak-reviewer",
        "Reviews changes for secrets exposure, PII in telemetry, insecure defaults, "
        "and supply-chain risks.",
        """\
You review changes for security and data-leak risks in the OpenTelemetry Demo.

## Review checklist

1. **Secrets in code** — no hardcoded passwords, API keys, or tokens?
2. **PII in telemetry** — span attributes, log fields, and metric labels must not
   contain names, email addresses, payment card data, or other PII.
3. **Environment variable hygiene** — sensitive values only via env vars; not logged
   at startup?
4. **Dependency updates** — new packages from trusted sources? No known CVEs?
5. **Docker image base** — no `latest` tags; pinned digests preferred?
6. **Open ports** — new exposed ports documented and intentional?
7. **Feature flags** — no flag that silently disables authentication or authorization?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths
- required fixes
""",
    ),
    (
        "docs-consistency-reviewer",
        "docs-consistency-reviewer",
        "Reviews docs/ and specs/ for accuracy, completeness, and consistency "
        "with actual service behavior after code changes.",
        """\
You review documentation in `docs/` and `specs/` for consistency with the codebase.

## Knowledge sources

- `docs/ai-knowledge/` — authoritative knowledge files
- `docs/features/` — feature behavior docs
- `docs/features/` — active SDD specs
- Service source code (read-only reference)

## Review checklist

1. **Accuracy** — do docs reflect the current code behavior?
2. **File paths** — are all cited file paths still valid?
3. **Service inventory** — is `service-inventory.json` up to date with the change?
4. **Communication overview** — does `communication/overview.md` reflect new
   dependencies or removed ones?
5. **Observability overview** — does `observability/overview.md` reflect new
   spans, metrics, or logs introduced by the change?
6. **Spec completeness** — if a spec was the input to this change, is the
   acceptance criteria verifiable and testable?
7. **No stale TODO** — no unresolved `TODO` / `FIXME` / `TBD` left in docs?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths
- required fixes
""",
    ),
    (
        "test-verification-reviewer",
        "test-verification-reviewer",
        "Verifies that changes include appropriate tests and that test commands "
        "pass before completion is claimed.",
        """\
You review changes to confirm that tests are present, correct, and passing.

## Review checklist

1. **Test coverage** — does the change include unit or integration tests for
   new behavior?
2. **Test commands** — are the correct build/test commands documented and runnable?
   (Reference: `docs/ai-knowledge/testing/overview.md` if present)
3. **Test isolation** — do tests rely on live external services (Kafka, PostgreSQL)
   without a clear setup step?
4. **OTel assertions** — if the change adds new spans or metrics, are there tests
   that assert those signals are emitted?
5. **No fake evidence** — completion must not be claimed without actual command
   output showing tests pass.
6. **Load-generator coverage** — if user-facing behavior changed, does
   `src/load-generator/locustfile.py` need updating?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths
- required fixes
""",
    ),
    (
        "knowledge-curator",
        "knowledge-curator",
        "Documentation and bootstrap agent responsible for keeping docs/ai-knowledge/ "
        "accurate and up to date after any significant code or architecture change.",
        """\
You are the knowledge-curator agent.

## Responsibilities

After any significant code, architecture, or instrumentation change, update the
canonical knowledge files so future agents have accurate context.

## Knowledge files you own

- `docs/ai-knowledge/services/*.md` — one per service
- `docs/ai-knowledge/services/service-inventory.json` — machine-readable inventory
- `docs/ai-knowledge/communication/overview.md`
- `docs/ai-knowledge/observability/overview.md`
- `docs/ai-knowledge/frontend/overview.md` (if present)
- `docs/ai-knowledge/testing/overview.md` (if present)

## Rules

- Do not edit production code.
- Write only under `docs/`, `specs/bootstrap-report.md`, or `.sdd/evidence/`.
- Mark unknowns explicitly — never invent architecture.
- Keep `overview.md` files short (summary + key facts); put details in service-specific files.
- Cite exact file paths when documenting behavior.
- After updating, verify that all file paths cited in docs still exist on disk.
""",
    ),
]


# ---------------------------------------------------------------------------
# Language reviewer template
# ---------------------------------------------------------------------------
def render_language_reviewer(lang_slug: str, lang: str, services: list[dict]) -> str:
    """Return Markdown content for a per-language technical reviewer agent."""
    agent_name = f"technical-{lang_slug}-reviewer"
    svc_list = ", ".join(s["name"] for s in services)
    service_dirs = " ".join(f"`src/{s['name']}/`" for s in services)

    description = (
        f"Reviews {lang} code changes in the OpenTelemetry Demo for correctness, "
        f"idiomatic style, OTel instrumentation, and test coverage. "
        f"Covers: {svc_list}."
    )

    knowledge_lines = "\n".join(
        f"- `docs/ai-knowledge/services/{s['name']}.md`" for s in services
    )

    return f"""\
---
name: {agent_name}
description: {description}
tools: Read, Grep, Glob, Bash
model: sonnet
---

You perform technical code review for {lang} services in the OpenTelemetry Demo.

## Services in scope

{chr(10).join(f"- **{s['name']}** — `src/{s['name']}/`" for s in services)}

## Knowledge sources

{knowledge_lines}
- `docs/ai-knowledge/observability/overview.md`
- `docs/ai-knowledge/communication/overview.md`

## Review checklist

1. **Correctness** — does the logic match the stated intent?
2. **Idiomatic {lang}** — follows language conventions and project style?
3. **Error handling** — errors propagated or logged; no silent swallows?
4. **OTel instrumentation** — spans, metrics, and logs preserved and correctly named?
5. **Dependencies** — new imports justified? No unnecessary transitive deps added?
6. **Test coverage** — new behavior is tested; existing tests still pass?
7. **Documentation** — public APIs / significant behavior changes documented?

## Output format

Return:
- verdict: `pass` | `needs-changes` | `blocked`
- findings by severity (critical / warning / info)
- exact file paths and line numbers where relevant
- required fixes for anything non-passing

## Rules

- Do not edit any files.
- Base findings on code evidence, not assumptions.
- Flag instrumentation regressions as **critical**.
"""


# ---------------------------------------------------------------------------
# Cross-cutting reviewer renderer
# ---------------------------------------------------------------------------
def render_cross_cutting(slug: str, name: str, description: str, body: str) -> str:
    """Return Markdown content for a cross-cutting reviewer agent."""
    return f"""\
---
name: {name}
description: {description}
tools: Read, Grep, Glob, Bash
model: sonnet
---

{body.rstrip()}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reviewer agent files from service-inventory.json"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing agent files",
    )
    args = parser.parse_args()

    if not INVENTORY_PATH.exists():
        print(f"ERROR: inventory not found at {INVENTORY_PATH}", file=sys.stderr)
        sys.exit(1)

    with INVENTORY_PATH.open() as f:
        services = json.load(f)

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0

    # ------------------------------------------------------------------
    # 1. Language reviewers (exclude N/A infrastructure)
    # ------------------------------------------------------------------
    lang_groups: dict[str, list[dict]] = defaultdict(list)
    for svc in services:
        lang = svc.get("language", "N/A")
        if lang == "N/A":
            continue  # infrastructure services don't get a language reviewer
        slug = LANGUAGE_TO_SLUG.get(
            lang, lang.lower().replace(" ", "-").replace("/", "-")
        )
        lang_groups[slug].append(svc)

    # Build slug → lang mapping for display
    slug_to_lang: dict[str, str] = {}
    for svc in services:
        lang = svc.get("language", "N/A")
        if lang == "N/A":
            continue
        slug = LANGUAGE_TO_SLUG.get(
            lang, lang.lower().replace(" ", "-").replace("/", "-")
        )
        slug_to_lang[slug] = lang

    print("-- Language reviewers --")
    for slug, group in sorted(lang_groups.items()):
        out_path = AGENTS_DIR / f"technical-{slug}-reviewer.md"
        lang = slug_to_lang.get(slug, slug)

        if out_path.exists() and not args.force:
            # Read existing file so we preserve its content rather than overwriting
            print(
                f"  skip  {out_path.relative_to(REPO_ROOT)}"
                f"  (exists; use --force to overwrite)"
            )
            skipped += 1
            continue

        if out_path.exists() and args.force:
            # Read existing content as reference (log it, but we regenerate fresh)
            existing = out_path.read_text(encoding="utf-8")
            _ = existing  # available for future diff logic

        content = render_language_reviewer(slug, lang, group)
        out_path.write_text(content, encoding="utf-8")
        svc_names = ", ".join(s["name"] for s in group)
        print(f"  write  {out_path.relative_to(REPO_ROOT)}  [{svc_names}]")
        generated += 1

    # ------------------------------------------------------------------
    # 2. Cross-cutting reviewers
    # ------------------------------------------------------------------
    print("\n-- Cross-cutting reviewers --")
    for slug, name, description, body in CROSS_CUTTING_REVIEWERS:
        out_path = AGENTS_DIR / f"{slug}.md"

        if out_path.exists() and not args.force:
            # Read the existing file — this is the "use as template" behavior
            existing_content = out_path.read_text(encoding="utf-8")
            print(
                f"  skip  {out_path.relative_to(REPO_ROOT)}"
                f"  (exists; using existing as template — pass --force to regenerate)"
            )
            # Print a brief summary of what the existing file says for traceability
            first_line = next(
                (
                    ln.strip()
                    for ln in existing_content.splitlines()
                    if ln.strip() and not ln.startswith("---")
                ),
                "(no content preview)",
            )
            print(f"         existing first content line: {first_line[:80]}")
            skipped += 1
            continue

        content = render_cross_cutting(slug, name, description, body)
        out_path.write_text(content, encoding="utf-8")
        print(f"  write  {out_path.relative_to(REPO_ROOT)}")
        generated += 1

    print(f"\nDone. Generated: {generated}  Skipped: {skipped}")


if __name__ == "__main__":
    main()
