---
description: Execute an approved SDD plan using Superpowers-style subagent-driven
  development with per-task review loops.
argument-hint: "[feature-area/change-slug]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Execute

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

## Purpose

Execute an approved implementation plan task by task.

Semantic review happens here, not in hooks.

## Paths

Base:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Required files:

- `01-design.md`
- `02-design-review.md`
- `03-implementation-plan.md`
- `04-plan-review.md`
- `tasks/*.md`

## Use method references

- `.claude/skills/sdd-execute/upstream/superpowers-subagent-driven-development.md`
- `.claude/skills/sdd-execute/upstream/superpowers-test-driven-development.md`
- `.claude/skills/sdd-execute/upstream/superpowers-requesting-code-review.md`
- `docs/ai-knowledge/validation/sdd-review-loop.md`
- `docs/ai-knowledge/validation/sdd-agent-routing.md`
- `docs/ai-knowledge/validation/sdd-evidence-format.md`
- `docs/ai-knowledge/validation/sdd-human-escalation.md`
- `.sdd/pipeline.md`
- `.sdd/pipeline.json`

## Core model

One fresh implementer subagent per task.

Dispatcher model: `sonnet` (per CLAUDE.md instruction for implementers).

Reviewer subagents: default model.

Semantic review is orchestrated by the sdd-orchestrator, not by hooks.

## Per-task execution loop

For each task in `tasks/*.md`:

### Step 1 — Extract context

- Read full task text.
- Read relevant excerpts from `01-design.md` and `03-implementation-plan.md`.
- Note the task's `owner_agent`, `services_touched`, `telemetry_impact`,
  `sensitive_data_impact`, `contracts_touched`.

### Step 2 — Dispatch implementer

Dispatch the task's `owner_agent` (fresh subagent, model: sonnet) with:

- full task text,
- design context relevant to this task,
- plan context relevant to this task,
- instruction to use TDD for any behavior changes,
- instruction to run relevant verification commands,
- instruction to self-review before reporting,
- instruction to fix self-review findings before reporting,
- instruction to report structured status:
  `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`

Implementer report must include:

```text
Status: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
Files changed: [list]
Tests added: [list]
Commands run: [command | exit code | output summary]
Self-review: completeness | quality | discipline | testing | concerns
```

### Step 3 — Handle implementer status

**DONE**: proceed to review.

**DONE_WITH_CONCERNS**: inspect concerns before review. If a concern affects
architecture, scope, design, or plan — escalate to user before review.

**NEEDS_CONTEXT**: provide context if the orchestrator can supply it; re-dispatch.
Ask user only if the context requires a human decision.

**BLOCKED**: assess whether to provide context, split the task, use a stronger
model, or ask user if the plan is wrong.

### Step 4 — Run review sequence

Dispatch reviewers in order. Each reviewer reads actual code — they must not
trust the implementer report alone.

**Always required:**

1. `spec-compliance-reviewer`
   - Does the implementation match the design and plan?
   - Code quality review must NOT run until this passes.

2. `domain-{service}-expert` (for each service with changed logic)
   - Is the domain behavior correct?

3. `technical-{language}-reviewer` (for each changed language runtime)
   - Is the implementation idiomatically correct and runtime-safe?

4. `observability-reviewer` (always — mandatory for this project)
   - Span names, attributes, metric types, trace context propagation.

5. `security-data-leak-reviewer` (always — mandatory for this project)
   - PII in span attributes, log bodies, Kafka messages.

6. `test-verification-reviewer` (always)
   - Trace tests cover new spans; Cypress tests cover new UI behavior.

**Conditional:**

7. `service-contract-reviewer` — if `contracts_touched` is non-empty or
   `pb/demo.proto` was changed.

8. `distributed-flow-reviewer` — if the change introduces or modifies
   cross-service calls.

9. `frontend-ui-kit-reviewer` — if `src/frontend/` was changed.

**Final:**

10. `code-quality-reviewer` — only after spec-compliance-reviewer passes.

11. `docs-consistency-reviewer` — final gate; checks feature docs and
    ai-knowledge accuracy.

### Step 5 — Arbitrate findings

For every finding from every reviewer:

- **accept** — send finding to implementer for fix,
- **reject** — record rationale; do not apply the change,
- **debate once** — argue back with evidence; if unresolved, escalate to user,
- **ask user** — when the decision requires product, architecture, or
  security judgment.

### Step 6 — Re-review after fixes

After implementer applies accepted findings:

- Re-run the reviewer(s) that had failing findings.
- Do not re-run reviewers whose findings were all resolved.

### Step 7 — Write task evidence

Write evidence file at:

```text
docs/features/{feature-area}/changes/{change-slug}/tasks/{task-id}.evidence.md
```

Use template: `docs/features/_template/changes/_template/tasks/task-evidence-template.md`

### Step 8 — Continue

Mark task complete. Move to next task.

Do not ask "should I continue?" when an approved plan has remaining tasks.

## Human escalation

Stop and ask user when:

- product behavior or scope needs clarification,
- service boundary changes not in the plan,
- public contract changes not in the plan,
- telemetry semantics change not in the plan,
- sensitive data handling not covered,
- reviewer disagreement affects architecture, security, or product,
- plan is wrong,
- verification repeatedly fails with no new information.

## After all tasks

1. Run final whole-change review.
2. Proceed to `/sdd-verify {feature-area}/{change-slug}`.
