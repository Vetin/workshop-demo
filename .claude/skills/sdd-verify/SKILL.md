---
description: Run final automatic, browser/manual, trace, and documentation
  verification before claiming completion.
argument-hint: "[feature-area/change-slug]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Verify

Input:

$ARGUMENTS

Expected format: `{feature-area}/{change-slug}`

## Purpose

Prove the feature or bug fix works before claiming completion.

## Paths

Base:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Verification report:

```text
docs/features/{feature-area}/changes/{change-slug}/verification/final-verification-report.md
```

## Use method reference

- `.claude/skills/sdd-verify/upstream/superpowers-verification-before-completion.md`

## Required inputs

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- docs/features/{feature-area}/changes/{change-slug}/03-implementation-plan.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/*.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/*.evidence.md
- docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md
- docs/ai-knowledge/local-runbook/overview.md

## Verification rule

Before claiming anything is complete:

1. Identify what command or manual check proves the claim.
2. Run the command or perform the check fresh.
3. Read the actual output.
4. Confirm the output matches the claim.

Do not accept stale output from a previous run as evidence.

## Run all verification types

### Automatic verification

- Run unit tests for changed services.
- Run trace tests: `make run-tracetesting` (or service-specific equivalent).
- Run lint for changed languages.
- Record: command, exit code, output summary.

### Manual / browser verification

Follow each case in `verification/manual-test-cases.md`:

- Start the demo (`make start` or `make start-minimal`).
- Execute steps.
- Confirm expected results.
- Record: pass | fail | blocked.

### Observability verification

- Open Jaeger UI: `http://localhost:8080/jaeger/ui/`
- Find a trace that exercises the changed flow.
- Confirm:
  - new spans exist with correct names,
  - required span attributes are present,
  - trace context propagates across service boundaries,
  - no orphaned spans.
- Record: span name, attributes observed, screenshot path if applicable.

### Documentation verification

- Confirm `docs/features/{feature-area}/overview.md` reflects current behavior.
- Confirm `docs/features/{feature-area}/detail.md` reflects current behavior.
- Run `docs-consistency-reviewer` if docs were updated during execute.

### Final spec compliance review

- Run `spec-compliance-reviewer` against all changes as a whole.

## If verification fails

1. Create a follow-up task under:

   ```text
   docs/features/{feature-area}/changes/{change-slug}/tasks/
   ```

2. Fix through the `/sdd-execute` loop.
3. Re-run the specific failed verification — do not accept a partial pass.

## Write verification report

Write `verification/final-verification-report.md` with:

- automatic test results (command, exit code, summary),
- manual test case results (pass | fail | blocked per case),
- observability check results (spans confirmed, attributes confirmed),
- documentation check result,
- spec compliance review result,
- overall verdict: `pass` | `fail` | `conditional`.

## Output

- verification verdict,
- path to `final-verification-report.md`,
- any remaining issues,
- recommended next command:

  `/sdd-finalize {feature-area}/{change-slug}`
