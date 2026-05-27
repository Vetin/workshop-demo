---
description: Review an SDD design document using domain, architecture,
  observability, security, and external reviewers before planning.
argument-hint: "[feature-area/change-slug]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Review Design

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

Example: `checkout-flow/gift-wrap-checkout`

## Purpose

Review the design before implementation planning.

Do not write production code.

## Paths

Design doc:

```text
docs/features/{feature-area}/changes/{change-slug}/01-design.md
```

Review output:

```text
docs/features/{feature-area}/changes/{change-slug}/02-design-review.md
```

## Required input

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- .sdd/pipeline.md
- .sdd/pipeline.json
- docs/ai-knowledge/validation/sdd-agent-routing.md
- docs/ai-knowledge/validation/sdd-external-review-policy.md

## Always-run reviewers

- `observability-reviewer` — verify telemetry impact is correctly described
- `security-data-leak-reviewer` — verify sensitive data handling is correct
- `docs-consistency-reviewer` — verify design is consistent with existing docs

## Conditional reviewers

- `domain-{service}-expert` — for each service the design touches
- `service-contract-reviewer` — if proto or HTTP API changes are proposed
- `distributed-flow-reviewer` — if cross-service call changes are proposed
- `frontend-ui-kit-reviewer` — if frontend UI changes are proposed
- External reviewer (Codex `design-plan-codex-review-subagent`) — for complex designs
  involving security, telemetry, or cross-service flows

## Review process

1. Spawn selected reviewers in parallel (read-only agents).
2. Ask each reviewer for findings only (no code yet).
3. Consolidate all findings into `02-design-review.md`.
4. For every finding, decide:
   - **accept** — apply change to `01-design.md`,
   - **reject** — record rationale in `02-design-review.md`,
   - **debate once** — argue back with evidence; if unresolved, escalate,
   - **ask user** — when the decision requires a product or architecture call.
5. Apply all accepted findings to `01-design.md`.
6. Ask user for any unresolved product / architecture / security decisions.
7. Mark design status: `approved` | `needs-changes` | `blocked`.

## Output

At the end, provide:

- design status,
- summary of key findings and decisions,
- unresolved user decisions if any,
- recommended next command:

  `/sdd-plan {feature-area}/{change-slug}`
