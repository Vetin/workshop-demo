---
description: Run final automatic, agentic browser/manual, E2E, trace, and documentation verification before claiming completion.
argument-hint: '[feature-area/change-slug]'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Verify

Input:

$ARGUMENTS

Expected format:

{feature-area}/{change-slug}

Example:

checkout-flow/gift-wrap-checkout

## Purpose

Prove the feature or bug fix works before claiming completion or giving the code to user review.

Verification order:

1. Automatic verification commands.
2. Agentic browser manual verification.
3. E2E test promotion from passed manual cases.
4. Run E2E tests.
5. Final verification reviewers.

## Paths

Base:

docs/features/{feature-area}/changes/{change-slug}/

Manual cases:

docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md

Browser verification report:

docs/features/{feature-area}/changes/{change-slug}/verification/browser-manual-verification-report.md

E2E test plan:

docs/features/{feature-area}/changes/{change-slug}/verification/e2e-test-plan.md

Final verification report:

docs/features/{feature-area}/changes/{change-slug}/verification/final-verification-report.md

## Use method reference

- .claude/skills/\_upstream-superpowers/verification-before-completion.md

## Read first

- docs/features/{feature-area}/overview.md
- docs/features/{feature-area}/detail.md
- docs/features/{feature-area}/changes/{change-slug}/01-design.md
- docs/features/{feature-area}/changes/{change-slug}/03-implementation-plan.md
- docs/features/{feature-area}/changes/{change-slug}/tasks/\*.evidence.md
- docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md
- docs/ai-knowledge/testing/detail.md
- docs/ai-knowledge/validation/sdd-evidence-format.md
- docs/ai-knowledge/validation/browser-verification.md
- docs/ai-knowledge/frontend/overview.md
- docs/ai-knowledge/ui-kit/overview.md

## Verification rule

Before claiming anything is complete:

1. Identify what command or browser check proves it.
2. Run the command/check fresh.
3. Read the output.
4. Check exit code or observed result.
5. Record evidence.
6. Only then state the claim.

## Stage 1 — Automatic verification

Run relevant checks from:

- docs/ai-knowledge/testing/detail.md
- 03-implementation-plan.md
- task evidence files

Possible checks:

- frontend tests
- integration tests
- service-specific tests
- trace-based tests
- contract checks
- lint/typecheck/build

Record:

- command,
- exit code,
- summarized output,
- evidence path.

If a check fails:

1. Create follow-up task under tasks/.
2. Fix through /sdd-execute.
3. Re-run failed check.

## Stage 2 — Agentic browser manual verification

Run browser-manual-verifier.

The browser verifier must use:

Default:

- agent-browser CLI

Allowed alternatives:

- Playwright MCP
- Chrome DevTools MCP

The verifier must execute:

docs/features/{feature-area}/changes/{change-slug}/verification/manual-test-cases.md

The verifier must write:

docs/features/{feature-area}/changes/{change-slug}/verification/browser-manual-verification-report.md

If browser verification fails:

1. Create follow-up task under tasks/.
2. Fix through /sdd-execute.
3. Re-run the failed manual case.
4. Do not proceed to E2E promotion until relevant manual cases pass.

If browser verification is blocked:

1. Record exact blocker.
2. Record required command or environment setup.
3. Ask user only if the environment cannot be started by the harness.

## Stage 3 — Promote manual cases into E2E tests

After browser manual verification passes, run e2e-test-author.

The E2E author reads:

- manual-test-cases.md
- browser-manual-verification-report.md
- implementation plan
- testing docs

It writes:

docs/features/{feature-area}/changes/{change-slug}/verification/e2e-test-plan.md

It should add or update E2E tests when:

- behavior is user-visible,
- behavior maps to acceptance criteria,
- behavior crosses service boundaries,
- behavior is regression-prone,
- manual verification found a bug during development.

It should not add E2E tests when:

- lower-level tests are more appropriate,
- selectors are unstable,
- local environment cannot support the case,
- the E2E would be flaky without app changes.

If E2E tests are not added, e2e-test-plan.md must explain why.

## Stage 4 — Run E2E tests

Run relevant E2E command from docs/ai-knowledge/testing/detail.md.

If no suitable E2E command exists:

1. Record this in e2e-test-plan.md.
2. Record proposed future setup.
3. Continue only if other verification covers the behavior.

If E2E tests fail:

1. Create follow-up task.
2. Fix through /sdd-execute.
3. Re-run E2E tests.
4. Re-run browser manual verification for affected cases.

## Stage 5 — E2E review

Run e2e-test-reviewer.

The reviewer checks:

- E2E cases match manual verification,
- tests cover acceptance criteria,
- tests use stable selectors or roles,
- tests are not too flaky or too broad,
- commands were run or waiver is explicit.

Fix accepted findings before continuing.

## Stage 6 — Final verification reviewers

Run:

- spec-compliance-reviewer
- test-verification-reviewer
- docs-consistency-reviewer

Add conditional reviewers if relevant:

- frontend-ui-kit-reviewer
- distributed-flow-reviewer
- service-contract-reviewer
- observability-reviewer
- security-data-leak-reviewer

## Final verification report

Create:

docs/features/{feature-area}/changes/{change-slug}/verification/final-verification-report.md

The report must include:

1. Automatic checks run.
2. Browser manual verification results.
3. Screenshots/snapshots collected.
4. E2E tests added or skipped.
5. E2E commands run.
6. Final reviewer results.
7. Verification gaps.
8. Waivers, if any.
9. Remaining risks.

## Evidence marker

If verification passes, create:

.sdd/evidence/latest-verification-pass

## Output

At the end, provide:

- verification report path,
- browser verification report path,
- E2E test plan path,
- commands run,
- pass/fail summary,
- recommended next command:

  /sdd-finalize {feature-area}/{change-slug}
