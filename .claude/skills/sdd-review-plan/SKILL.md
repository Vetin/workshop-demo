---
description: Review an implementation plan before execution using architecture,
  domain, technical, verification, and docs reviewers.
argument-hint: "[feature-area/change-slug]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Review Plan

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

## Purpose

Review the implementation plan before any production code is changed.

## Paths

Base:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Plan:

```text
03-implementation-plan.md
```

Plan review output:

```text
04-plan-review.md
```

## Required input

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- docs/features/{feature-area}/changes/{change-slug}/02-design-review.md
- docs/features/{feature-area}/changes/{change-slug}/03-implementation-plan.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/*.md
- docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md
- docs/ai-knowledge/validation/sdd-agent-routing.md
- .sdd/pipeline.md
- .sdd/pipeline.json

## Reviewers

Always run:

- `docs-consistency-reviewer` — plan is consistent with existing feature docs
- `test-verification-reviewer` — test strategy covers new spans and behavior
- `observability-reviewer` — telemetry changes are correctly planned

Conditional:

- `domain-{service}-expert` — for each service with logic changes
- `technical-{language}-reviewer` — for each language runtime changed
- `service-contract-reviewer` — if proto or API contract changes are in the plan
- `distributed-flow-reviewer` — if cross-service call changes are planned
- `frontend-ui-kit-reviewer` — if frontend changes are in the plan

External review (Codex `impl-plan-codex-review-subagent`):
- for plans with 4+ tasks, cross-service changes, or security/telemetry changes.

## What reviewers check

Each reviewer answers:

1. Is every task achievable by one implementer subagent?
2. Does every task have an owner agent?
3. Does every task have reviewer agents listed?
4. Are tests defined before implementation (TDD order)?
5. Are contract changes explicit (proto fields, HTTP routes)?
6. Are telemetry changes explicit (span names, attributes)?
7. Is sensitive data handling documented?
8. Is the verification plan executable?
9. Are docs-to-update paths explicit per task?
10. Is the definition of done clear and measurable?

## Review process

1. Spawn selected reviewers in parallel.
2. Consolidate findings into `04-plan-review.md`.
3. For every finding:
   - **accept** — update plan or task files,
   - **reject** — record rationale,
   - **debate once** — argue with evidence; escalate if unresolved,
   - **ask user** — when the decision requires a product or architecture call.
4. Mark plan status: `approved` | `needs-changes` | `blocked`.

## Output

At the end, provide:

- plan status,
- summary of key findings and changes applied,
- unresolved user decisions if any,
- recommended next command:

  `/sdd-execute {feature-area}/{change-slug}`
