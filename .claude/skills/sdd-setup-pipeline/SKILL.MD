---
description: Create the SDD delivery pipeline from extracted project docs, generated agents, validation categories, and upstream methodology references.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Setup Pipeline

Goal:
Create the SDD delivery pipeline using the project intelligence produced during Setup 1.

Do not modify production code.

## Required inputs

Read:

- docs/ai-knowledge/architecture/*
- docs/ai-knowledge/services/*
- docs/ai-knowledge/communication/*
- docs/ai-knowledge/frontend/*
- docs/ai-knowledge/ui-kit/*
- docs/ai-knowledge/testing/*
- docs/ai-knowledge/observability/*
- docs/ai-knowledge/validation/*
- docs/ai-knowledge/agents/*
- docs/ai-knowledge/learning/*
- docs/features/*
- .claude/agents/*
- .claude/skills/_upstream-superpowers/*
- .claude/skills/_upstream-ecc/*

## Create or update

Pipeline docs:

- .sdd/pipeline.md
- .sdd/pipeline.json

Feature/change templates:

- docs/features/_template/overview.md
- docs/features/_template/detail.md
- docs/features/_template/changes/_template/01-design.md
- docs/features/_template/changes/_template/02-design-review.md
- docs/features/_template/changes/_template/03-implementation-plan.md
- docs/features/_template/changes/_template/04-plan-review.md
- docs/features/_template/changes/_template/tasks/task-template.md
- docs/features/_template/changes/_template/tasks/task-evidence-template.md
- docs/features/_template/changes/_template/verification/manual-test-cases.md
- docs/features/_template/changes/_template/final-report.md

Validation docs:

- docs/ai-knowledge/validation/sdd-review-loop.md
- docs/ai-knowledge/validation/sdd-agent-routing.md
- docs/ai-knowledge/validation/sdd-evidence-format.md
- docs/ai-knowledge/validation/sdd-human-escalation.md
- docs/ai-knowledge/validation/sdd-external-review-policy.md

Skills:

- .claude/skills/sdd-start/SKILL.md
- .claude/skills/sdd-review-design/SKILL.md
- .claude/skills/sdd-plan/SKILL.md
- .claude/skills/sdd-review-plan/SKILL.md
- .claude/skills/sdd-execute/SKILL.md
- .claude/skills/sdd-verify/SKILL.md
- .claude/skills/sdd-finalize/SKILL.md

## Feature/change storage rule

Do not create specs/features.

All active SDD work belongs under:

docs/features/{feature-area}/changes/{change-slug}/

The stable feature documentation lives at:

docs/features/{feature-area}/overview.md
docs/features/{feature-area}/detail.md

## Important design rule

Do not make hooks the primary semantic review mechanism.

Use Superpowers-style subagent-driven development:

1. Fresh implementer subagent per task.
2. Implementer self-review before reporting.
3. Spec compliance review first.
4. Domain and technical reviews after spec compliance.
5. Code quality review after functional/spec reviews.
6. Docs consistency review before task completion.
7. Fix and re-review until approved.
8. Continue to the next task automatically.

Hooks may be used only for:
- dangerous command blocking,
- changed-file recording,
- optional final evidence guard.

## Pipeline must encode

1. Known feature areas.
2. Known docs sources.
3. Existing feature docs.
4. Available implementer agents.
5. Available domain expert agents.
6. Available reviewer agents.
7. Review order.
8. Human escalation rules.
9. Evidence requirements.
10. Self-learning update rules.
11. Final verification rules.

## After setup

Run harness-self-reviewer against:
- .sdd/pipeline.md
- .sdd/pipeline.json
- .claude/skills/sdd-*
- docs/features/_template/*
- docs/ai-knowledge/validation/sdd-*

Fix accepted findings.
