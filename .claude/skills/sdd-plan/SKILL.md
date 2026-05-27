---
description: Create an implementation plan, ADRs, task files, test strategy,
  verification plan, and definition of done.
argument-hint: '[feature-area/change-slug]'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Plan

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

## Purpose

Create a code-near implementation plan from an approved design.

Do not write production code.

## Paths

Base:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Create:

- `03-implementation-plan.md`
- `tasks/*.md` (one file per independent task)
- `verification/manual-test-cases.md`

## Required input

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- docs/features/{feature-area}/changes/{change-slug}/02-design-review.md
- .sdd/pipeline.md
- .sdd/pipeline.json
- docs/ai-knowledge/validation/sdd-agent-routing.md
- docs/ai-knowledge/validation/sdd-evidence-format.md
- docs/ai-knowledge/testing/detail.md (if exists)
- docs/ai-knowledge/services/* (relevant services)
- docs/ai-knowledge/communication/* (if cross-service)
- docs/ai-knowledge/frontend/* (if frontend)
- docs/ai-knowledge/ui-kit/* (if frontend UI)
- docs/ai-knowledge/observability/* (for telemetry changes)

Use upstream method reference:

- `.claude/skills/sdd-plan/upstream/superpowers-writing-plans.md`

## Plan must include

1. Architecture summary — why this approach, what alternatives were rejected.
2. ADRs — one per significant architecture decision.
3. Services changed — list with path and nature of change.
4. Contracts changed — proto fields, HTTP routes, Kafka message shape.
5. Frontend / UI-kit changes — components, routes, styled-components.
6. Telemetry changes — new spans, renamed attributes, new metrics.
7. Sensitive data handling — any new data flowing through spans or logs.
8. Test strategy — unit, integration, trace-based tests.
9. Manual / browser verification — user-facing steps to verify behavior.
10. Trace / observability verification — which Jaeger spans to check.
11. Task breakdown — ordered list of tasks.
12. Definition of done — explicit criteria for claiming completion.
13. Evidence requirements — which evidence files must exist.
14. Rollback / failure handling — how to recover if deployment fails.

## Each task file must include

```yaml
---
id: T-01
title:
status: todo
owner_agent:
reviewer_agents:
services_touched:
contracts_touched:
frontend_impact: false
ui_kit_impact: false
telemetry_impact: false
sensitive_data_impact: false
---
```

Plus sections:

- Goal
- Scope
- Relevant design excerpts
- Relevant plan excerpts
- Files likely touched
- Tests to write first (TDD — tests before implementation)
- Acceptance criteria
- Commands to run
- Docs to update
- Evidence file path

## Task design rule

Tasks must be small enough for one implementer subagent.

Do not mix in a single task:

- frontend and backend changes,
- contract changes and implementation,
- telemetry and UI changes,
- docs and production code.

Exception: when coupling is unavoidable — document it explicitly.

## Output

- implementation plan path,
- task list with task IDs and owner agents,
- verification plan path,
- recommended next command:

  `/sdd-review-plan {feature-area}/{change-slug}`
