# Stop Hook Policy

What happens when an implementer agent stops, and what the orchestrator does next.

Last updated: 2026-05-27

---

## SubagentStop Hook Behavior

When an implementer agent stops (task complete, blocked, or scope exceeded), the following gates run automatically via the SubagentStop hook before the orchestrator reads the result:

### Gate 1: Changed-file tracking
- `.sdd/evidence/changed-files.txt` is updated with the list of files modified during this implementation session.
- If this file is absent or empty when the hook runs, the implementation is treated as unverified and the orchestrator must re-dispatch with a verification requirement.

### Gate 2: Review router
- `.sdd/evidence/review-router.latest.json` is written (or overwritten) with the reviewer list computed from the changed files.
- The JSON structure contains: `changed_files`, `mandatory_reviewers`, `conditional_reviewers`, and `dispatch_order`.
- This file is the single source of truth for which reviewers the orchestrator dispatches next.

### Gate 3: Orchestrator reads and dispatches
- The orchestrator reads `review-router.latest.json` and dispatches each reviewer in the specified order.
- It does not dispatch reviewers that are not in the file. If a reviewer appears missing, the orchestrator investigates whether the changed-file tracking gate ran correctly.

---

## What Implementers Must NOT Do

Implementers are scoped to one language/service set. They must not:

- **Claim task completion themselves.** Completion is declared by the orchestrator after all mandatory reviewers pass, not by the implementer.
- **Skip leaving evidence.** Every stop must produce updated content in `.sdd/evidence/`. An implementer that stops without writing evidence has not completed its task.
- **Modify files outside their assigned service scope.** Each implementer has an explicit list of service paths. Writing to a path outside that list is a scope violation. If a cross-scope change is required, the implementer must stop, report the dependency, and let the orchestrator coordinate.
- **Self-approve OTel changes.** Even if the implementer believes the telemetry is correct, the observability-reviewer must run. Implementers do not have the authority to sign off on span attribute naming or semantic convention compliance.

---

## What Happens After Reviewers Run

The orchestrator follows this sequence after all dispatched reviewers return findings:

### Step 1: Arbitrate findings
Each reviewer finding is classified:
- **Blocker** — must be fixed before the feature is accepted. Re-dispatch the implementer with the specific blocker.
- **Major** — should be fixed. If multiple majors exist, batch them into a single re-dispatch to the implementer.
- **Minor** — optional improvement. Orchestrator notes it but does not block completion.
- **Suggestion** — informational. No action required.

### Step 2: Fix loop (if blockers or majors exist)
- The orchestrator re-dispatches the implementer with a targeted task: fix the listed blockers/majors only.
- The implementer stops, evidence is updated, reviewers for the changed files run again.
- This loop continues until no blockers or majors remain.

### Step 3: Knowledge update
- Once all mandatory reviewers pass with no blockers or majors, `knowledge-curator` runs.
- It updates `docs/ai-knowledge/` to reflect the new or changed service behavior.
- It also updates the communication flow map if service interactions changed.

### Step 4: Final documentation check
- `docs-consistency-reviewer` runs one final time against the updated knowledge docs.
- It verifies that the docs accurately describe the code that was actually implemented.
- If it finds a discrepancy, knowledge-curator is re-dispatched (not the implementer).

### Step 5: Completion evidence
- The orchestrator writes a completion record to `.sdd/evidence/` including:
  - Feature or bug ID
  - List of changed files (from changed-files.txt)
  - Reviewers that ran and their final verdicts
  - Date completed
- This evidence is required before the SDD workflow considers the task done.

---

## Evidence File Locations

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `.sdd/evidence/changed-files.txt` | SubagentStop hook | orchestrator, review-router | Tracks which files changed |
| `.sdd/evidence/review-router.latest.json` | SubagentStop hook | orchestrator | Specifies which reviewers to dispatch |
| `.sdd/evidence/<feature-id>-completion.json` | orchestrator | human, CI | Completion record for the feature |
| `.sdd/evidence/<feature-id>-findings.md` | orchestrator | human | Human-readable reviewer findings summary |
