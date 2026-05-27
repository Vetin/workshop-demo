# SDD Review Loop

Use this document during /sdd-execute.

## Core model

Semantic review is orchestrated by the main sdd-orchestrator agent.

Hooks may record changed files or block dangerous commands, but hooks do not replace semantic review.

## Per-task loop

For every task:

1. Orchestrator extracts full task text.
2. Orchestrator selects implementer.
3. Implementer works in fresh subagent context.
4. Implementer uses TDD for behavior changes.
5. Implementer runs relevant verification.
6. Implementer performs self-review.
7. Implementer fixes self-review findings.
8. Implementer reports:
   - DONE
   - DONE_WITH_CONCERNS
   - NEEDS_CONTEXT
   - BLOCKED

Then orchestrator runs reviews:

1. spec-compliance-reviewer
2. domain expert reviewers
3. technical reviewers
4. conditional cross-cutting reviewers
5. code-quality-reviewer
6. docs-consistency-reviewer

## Important ordering rule

Spec compliance review must pass before code quality review.


pec compliance review must pass before code quality review.ocking issues.

## Implementer status handling

DONE:
- proceed to spec comp- proceed to spec comp- proceed to spec comp- proceed to spec compew.
- if concern affects correctness/scope, fix before continuing.

NEEDS_CONTEXT:
- provide missing context and re-dispatch.
- ask user only if the context requires a human decision- ask user only if the context rxt,
- split task,
- use stronger model,
- or ask user- or ask user- or ask user- or ask user- or nd- or ask user- or ask user- or at,
- reject- reject-ionale,
- debate once,
- or ask user.

Accepted findings go back to theAccepted ter.
After fixes, the same reviewer re-checks.

####ompletion rule

A task is complete only when:
- implementer self-review passed,
- spec comp- spec comp- spec comired domain/technical reviewers passed,
- code quality review passed,
- docs consistency review passed,
- task evidence was written.
