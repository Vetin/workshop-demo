# Self-Learning Detail

## How to propose a knowledge update

Any agent that discovers a discrepancy between `docs/ai-knowledge/` and the
actual source code MUST propose an update rather than silently working around
stale knowledge.

### Proposal format

Append to `docs/ai-knowledge/learning/proposed-updates.md`:

```markdown
## [PENDING] {date} — {proposing-agent}

**Target file:** docs/ai-knowledge/services/{service}.md
**Change type:** correction | addition | deprecation
**Source evidence:** {exact file path}:{line number}

**Current text:**
> (exact quote from the current doc, or "missing")

**Proposed text:**
> (new text to replace or add)

**Justification:**
One sentence explaining what code changed and why this update is needed.
```

### Approval process

1. `knowledge-curator` reviews the proposal.
2. If accepted: applies the edit and moves the entry to `iteration-log.md`
   with status `[ACCEPTED]`.
3. If rejected: moves the entry to `rejected-updates.md` with status
   `[REJECTED]` and adds a reason.

## Drift detection

When an implementer subagent edits a service file, `post-edit-fast-feedback.sh`
records the changed file. After the task completes, the orchestrator SHOULD
ask the relevant domain-expert agent to verify the corresponding
`docs/ai-knowledge/services/{service}.md` is still accurate.

Reviewers are expected to flag documentation drift as a finding in their review
output. The `docs-consistency-reviewer` specifically checks this.

## Machine-readability requirements

`service-inventory.json` is consumed by:
- `scripts/ai/generate-domain-agents.py`
- `scripts/ai/review-router.py`
- `scripts/ai/generate-implementer-agents.py`

Any update to `service-inventory.json` MUST preserve the JSON schema:
```json
{
  "name": "string",
  "language": "string",
  "framework": "string",
  "port": "number|null",
  "dockerfile": "string|null",
  "entrypoint": "string|null",
  "dependencies": ["string"],
  "communication_type": ["string"],
  "otel_instrumentation": "string"
}
```

Changes to service-inventory.json require human review (not just
knowledge-curator approval) because they affect agent generation.

## Feature flag update rules

`src/flagd/demo.flagd.json` is the authoritative flag source.
`docs/features/feature-flags.md` must mirror it after any flag change.

The `observability-reviewer` verifies this during every review pass that
touches flagd files.

## Iteration cadence

- After every completed implementation task: update service doc if behavior changed
- After every proto change: update `communication/proto-contracts.md`
- After every new feature: update `docs/features/{feature}.md`
- After every new metric/span: update `observability/detail.md`
- Quarterly: re-run `repo-cartographer` and diff against `architecture/overview.md`
