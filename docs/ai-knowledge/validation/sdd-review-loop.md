# SDD Review Loop

Use this document during `/sdd-execute`.

## Core model

Semantic review is orchestrated by the sdd-orchestrator agent.

Hooks may record changed files or block dangerous commands, but hooks do not
replace semantic review.

## Per-task loop

For every task:

1. Orchestrator extracts full task text and relevant context.
2. Orchestrator selects implementer from task `owner_agent`.
3. Implementer works in a fresh subagent context (model: sonnet).
4. Implementer uses TDD for behavior changes.
5. Implementer runs relevant verification.
6. Implementer performs self-review.
7. Implementer fixes self-review findings.
8. Implementer reports structured status:
   - `DONE`
   - `DONE_WITH_CONCERNS`
   - `NEEDS_CONTEXT`
   - `BLOCKED`

Then orchestrator runs reviews in order:

1. `spec-compliance-reviewer` (always first)
2. `domain-{service}-expert` (if service logic changed)
3. `technical-{language}-reviewer` (per changed language)
4. `observability-reviewer` (always — mandatory for this project)
5. `security-data-leak-reviewer` (always — mandatory for this project)
6. `test-verification-reviewer` (always)
7. `service-contract-reviewer` (if proto/API changed)
8. `distributed-flow-reviewer` (if cross-service call changed)
9. `frontend-ui-kit-reviewer` (if `src/frontend/` changed)
10. `code-quality-reviewer` (only after spec compliance passes)
11. `docs-consistency-reviewer` (final gate)

## Important ordering rule

`code-quality-reviewer` must not run until `spec-compliance-reviewer` passes.

## Implementer status handling

**DONE**: proceed to review immediately.

**DONE_WITH_CONCERNS**: inspect concerns before review. If a concern affects
architecture, scope, design, or plan — escalate to user before dispatching
reviewers.

**NEEDS_CONTEXT**: provide more context if the orchestrator can supply it and
re-dispatch. Ask user only if the context requires a human decision.

**BLOCKED**: assess whether to:

- provide more context,
- split the task,
- use a stronger model,
- or ask user if the plan is wrong.

## Review finding handling

For every finding from any reviewer:

- **accept** — send to implementer for fix,
- **reject** — record rationale; document in evidence file,
- **debate once** — argue back with evidence; if still unresolved, escalate,
- **ask user** — when decision requires product, architecture, or security call.

Accepted findings go back to the implementer.

After fixes, re-run only the reviewer(s) with failing findings.

## Task completion criteria

A task is complete only when:

- implementer self-review passed,
- spec-compliance-reviewer passed,
- required domain/technical/observability/security reviews passed,
- test-verification-reviewer passed,
- code-quality-reviewer passed,
- docs-consistency-reviewer passed,
- task evidence file was written.
