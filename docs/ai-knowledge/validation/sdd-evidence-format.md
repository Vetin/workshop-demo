# SDD Evidence Format

Every completed task must produce an evidence file.

Location:

```text
docs/features/{feature-area}/changes/{change-slug}/tasks/{task-id}.evidence.md
```

Use the template at:

```text
docs/features/_template/changes/_template/tasks/task-evidence-template.md
```

## Required sections

### Task

- id: (e.g., T-01)
- title: (task title from task file)
- owner implementer: (agent name)
- status: done | done-with-concerns | blocked

### Files changed

List each file changed with a one-line description of what changed.

### Tests added or updated

List each test file. If no tests added, explain why (e.g., "pure config change,
no behavior").

### Commands run

Format: `command | exit code | output summary`

Example:

```text
make run-tracetesting | 0 | 3 tests passed, 0 failed
go test ./... | 0 | All 12 tests pass
```

### Implementer self-review

- completeness: did the task achieve its full stated goal?
- quality: idiomatic code, error handling, no shortcuts?
- discipline: TDD followed where required?
- testing: tests cover new behavior?
- concerns: anything flagged for reviewer attention.

### Spec compliance review

- reviewer: spec-compliance-reviewer
- verdict: pass | fail | conditional
- findings: (list or "none")
- fixes applied: (list or "n/a")

### Domain expert review

- reviewers: (list of domain-{service}-expert agents dispatched)
- verdict: pass | fail | conditional | n/a
- findings: (list or "none" or "n/a — no domain logic changed")
- fixes applied: (list or "n/a")

### Technical review

- reviewers: (list of technical-{language}-reviewer agents dispatched)
- verdict: pass | fail | conditional
- findings: (list or "none")
- fixes applied: (list or "n/a")

### Observability review

- reviewer: observability-reviewer
- verdict: pass | fail | conditional
- findings: (list or "none")
- fixes applied: (list or "n/a")

### Security / data leak review

- reviewer: security-data-leak-reviewer
- verdict: pass | fail | n/a
- findings: (list or "none" or "n/a — no PII paths touched")
- fixes applied: (list or "n/a")

### Cross-cutting review

- reviewers: (list of conditional reviewers dispatched, or "none")
- verdict: pass | fail | n/a
- findings: (list or "n/a")
- fixes applied: (list or "n/a")

### Test verification review

- reviewer: test-verification-reviewer
- verdict: pass | fail | conditional
- findings: (list or "none")
- fixes applied: (list or "n/a")

### Code quality review

- reviewer: code-quality-reviewer
- verdict: pass | fail | conditional
- findings: (list or "none")
- fixes applied: (list or "n/a")

### Docs consistency review

- reviewer: docs-consistency-reviewer
- verdict: pass | fail | conditional
- docs updated: (list paths updated, or "none required")
- docs intentionally not updated: (reason if any)

### Accepted findings

Format: `{id} | {reviewer} | {change made}`

### Rejected findings with rationale

Format: `{id} | {reviewer} | {rationale for rejection}`

### Remaining risks

### Follow-up tasks
