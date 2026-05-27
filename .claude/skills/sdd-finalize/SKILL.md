---
description: Finalize SDD iteration by updating feature docs, AI knowledge docs,
  learning logs, evidence markers, and final report.
argument-hint: "[feature-area/change-slug]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Finalize

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

## Purpose

Convert active SDD work into durable project knowledge.

## Paths

Change folder:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Stable feature docs:

```text
docs/features/{feature-area}/overview.md
docs/features/{feature-area}/detail.md
```

Final report:

```text
docs/features/{feature-area}/changes/{change-slug}/final-report.md
```

## Required before finalization

All of these must be true:

- All planned tasks are marked complete.
- All task evidence files exist under `tasks/*.evidence.md`.
- `spec-compliance-reviewer` passed on all tasks.
- `observability-reviewer` passed.
- `security-data-leak-reviewer` passed.
- `verification/final-verification-report.md` exists with verdict `pass`
  or user explicitly waived verification with documented rationale.
- `docs-consistency-reviewer` passed.

If any condition is not met, return the reason and do not finalize.

## Read

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- docs/features/{feature-area}/changes/{change-slug}/03-implementation-plan.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/*.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/*.evidence.md
- docs/features/{feature-area}/changes/{change-slug}/verification/final-verification-report.md
- docs/ai-knowledge/services/* (for affected services)
- docs/ai-knowledge/communication/* (if communication changed)
- docs/ai-knowledge/observability/* (if telemetry changed)
- docs/ai-knowledge/validation/sdd-evidence-format.md

## Update stable feature docs

Update `docs/features/{feature-area}/overview.md`:

- Reflect new or changed behavior in plain language.
- Update "Services involved" if services changed.
- Add a link to the change folder in "Related changes".

Update `docs/features/{feature-area}/detail.md`:

- Update "Behavior" sections that changed.
- Update "Edge cases" if new edge cases were handled.
- Update "Contracts" if proto or API changed.
- Update "Telemetry" if spans or attributes changed.
- Update "Tests" if new tests were added.

## Update AI knowledge docs

Run `knowledge-curator` to update:

- `docs/ai-knowledge/services/{service}.md` — for each service that changed.
- `docs/ai-knowledge/communication/` — if inter-service communication changed.
- `docs/ai-knowledge/observability/` — if telemetry instrumentation changed.

Then run `docs-consistency-reviewer` to verify the knowledge-curator output.

If docs-consistency-reviewer finds issues:
- re-dispatch knowledge-curator, not the implementer.

## Run finalization reviewers

1. `knowledge-curator` — update ai-knowledge docs to reflect current behavior.
2. `docs-consistency-reviewer` — verify knowledge-curator output is accurate.
   If issues found, re-dispatch knowledge-curator (not the implementer).
3. Final whole-change `code-quality-reviewer` if not already run in execute.

## Write final report

Write `final-report.md` using the template at:

`docs/features/_template/changes/_template/final-report.md`

Include:

- summary of what was built or fixed,
- requirements covered (from acceptance criteria in design),
- tasks completed (task IDs),
- tests added or updated,
- verification evidence references,
- review evidence references,
- stable feature docs updated (yes | no, paths),
- AI knowledge updated (yes | no, paths),
- user decisions made during the change,
- known limitations,
- follow-up work items,
- final status: `complete` | `incomplete` | `blocked`.

## Create evidence markers

If all reviews and verification pass, create:

- `.sdd/evidence/latest-spec-review-pass`
- `.sdd/evidence/latest-code-quality-pass`
- `.sdd/evidence/latest-verification-pass`

Each marker file content:

```text
{feature-area}/{change-slug}
{date}
```

## Self-learning update

Record in `docs/ai-knowledge/learning/iteration-log.md`:

- change delivered,
- date,
- services affected,
- patterns that worked well,
- patterns that caused rework.

Propose doc improvements in `docs/ai-knowledge/learning/proposed-updates.md`.

## Keep change folder

Do not delete the change folder.

It is the delivery history for this change.

## Output

- final status,
- paths updated,
- evidence markers created,
- recommended next action (new `/sdd-start` or done).
