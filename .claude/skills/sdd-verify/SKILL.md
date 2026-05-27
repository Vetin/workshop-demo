---
description: Verify an SDD change before user review: run automatic checks, start app if needed, perform browser verification, promote cases to E2E, run E2E, loop on failures, and write evidence.
argument-hint: "[feature-area/change-slug] [--stage automatic|browser|e2e|final] [--resume]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Verify

Input:

$ARGUMENTS

Expected format:

```text
{feature-area}/{change-slug}

Example:

checkout-flow/gift-wrap-checkout
Purpose

Prove the change works before user review or finalization.

Default command:

/sdd-verify {feature-area}/{change-slug}

runs the full verification pipeline.

Stage flags are only for demo/debug:

--stage automatic
--stage browser
--stage e2e
--stage final
--resume
Required paths

Change folder:

docs/features/{feature-area}/changes/{change-slug}/

Expected inputs:

01-design.md
03-implementation-plan.md
tasks/*.evidence.md
verification/manual-test-cases.md

Expected outputs:

verification/browser-manual-verification-report.md
verification/e2e-test-plan.md
verification/final-verification-report.md
.sdd/evidence/latest-verification-pass
Read first

Read these before acting:

docs/features/{feature-area}/overview.md
docs/features/{feature-area}/detail.md
docs/features/{feature-area}/changes/{change-slug}/01-design.md
docs/features/{feature-area}/changes/{change-slug}/03-implementation-plan.md
docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md

docs/ai-knowledge/testing/detail.md
docs/ai-knowledge/local-runbook/detail.md
docs/ai-knowledge/validation/browser-verification.md
docs/ai-knowledge/validation/sdd-evidence-format.md
docs/ai-knowledge/validation/sdd-agent-routing.md
docs/ai-knowledge/validation/sdd-human-escalation.md

Use this method reference:

.claude/skills/_upstream-superpowers/verification-before-completion.md
Core rule

Do not claim completion without fresh evidence.

For every claim:

Identify what proves it.
Run the command or browser check.
Read the result.
Record evidence.
Only then claim pass/fail.
Full verification flow

When no --stage flag is provided, run all stages:

1. Automatic checks
2. Browser/manual verification
3. E2E promotion
4. E2E execution
5. Final verification review
6. Final verification report

Continue automatically until verification passes or a real human decision is required.

Do not ask “should I continue?”

Stage 1 — Automatic checks

Run relevant checks from:

docs/ai-knowledge/testing/detail.md
03-implementation-plan.md
tasks/*.evidence.md

Examples:

frontend tests
integration tests
service-specific tests
contract checks
trace-based tests
lint/typecheck/build

Record:

command
exit code
summary
evidence path

If automatic checks fail, classify:

application bug
test bug
environment issue
flaky test
missing setup

Then:

application/test bug → create fix task, fix via /sdd-execute loop, rerun failed check
environment issue → try runbook, ask user only if unresolved
flaky test → stabilize test or document blocker
Stage 2 — Browser/manual verification

Run:

browser-manual-verifier

The verifier must:

Read the local runbook.
Check if the app is running.
Start the app if needed.
Wait for readiness.
Run manual browser cases.
Capture screenshots/snapshots.
Write browser verification report.

Default browser tool:

agent-browser

Allowed alternatives:

Playwright MCP
Chrome DevTools MCP

Browser report path:

docs/features/{feature-area}/changes/{change-slug}/verification/browser-manual-verification-report.md

If browser verification fails:

capture evidence
create fix task
fix via /sdd-execute loop
rerun affected automatic checks
rerun failed browser case

If browser verification is blocked:

record blocker
record failing command/logs
try runbook fix
ask user only if harness cannot resolve environment issue
Stage 3 — E2E promotion

After browser verification passes, run:

e2e-test-author

It must decide which passed manual cases deserve E2E coverage.

Write:

docs/features/{feature-area}/changes/{change-slug}/verification/e2e-test-plan.md

Add E2E tests when behavior is:

user-visible
acceptance-criteria-driven
cross-service
regression-prone
previously failed during manual verification

Do not add E2E tests when:

lower-level tests are better
selectors are unstable
local environment cannot support it
test would be flaky

Skipped E2E coverage requires rationale.

Stage 4 — E2E execution

Run the relevant E2E command from:

docs/ai-knowledge/testing/detail.md

If E2E fails, classify:

application bug
E2E test bug
selector instability
timing/flakiness
missing setup
environment issue

Then fix the correct layer:

application bug → fix via /sdd-execute, rerun browser case and E2E
test bug → fix E2E, run e2e-test-reviewer, rerun E2E
flaky test → stabilize selectors/waits/setup, rerun E2E
environment issue → use runbook, ask user only if unresolved

Run:

e2e-test-reviewer

before accepting new or changed E2E tests.

Stage 5 — Final verification review

Run:

spec-compliance-reviewer
test-verification-reviewer
docs-consistency-reviewer

Add conditional reviewers from:

docs/ai-knowledge/validation/sdd-agent-routing.md

Examples:

frontend-ui-kit-reviewer
distributed-flow-reviewer
service-contract-reviewer
observability-reviewer
security-data-leak-reviewer

Fix accepted findings before final report.

Stage 6 — Final report

Create:

docs/features/{feature-area}/changes/{change-slug}/verification/final-verification-report.md

Report must include:

automatic checks run
browser verification result
app startup evidence
screenshots/snapshots
E2E tests added or skipped
E2E command results
final reviewer results
waivers
remaining risks
follow-up tasks created and resolved

If verification passes, create:

.sdd/evidence/latest-verification-pass
Output

Return:

verification status
final verification report path
browser report path
E2E test plan path
commands run
follow-up tasks created/resolved
remaining risks
recommended next command

Recommended next command after success:

/sdd-finalize {feature-area}/{change-slug}

```
