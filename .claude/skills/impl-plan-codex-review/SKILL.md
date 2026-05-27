---
name: impl-plan-codex-review
description: Use after writing an implementation plan to auto-review it with Codex agents (structure + correctness reviewers) in a cooperative disagreement model, followed by a fresh generalist pass
---

<!--
LOCAL PROJECT OVERRIDE
This file shadows the global skill at ~/.claude/skills/impl-plan-codex-review/SKILL.md.
Edit THIS file to change review behavior for this project.

Extension points:
  - Reviewer prompts: .claude/skills/impl-plan-codex-review/*-reviewer-prompt.md
    Update these and re-run `codex profile set` to apply project-specific criteria.
  - Script location: scripts remain at ~/.claude/skills/impl-plan-codex-review/
    To copy scripts locally, update the bash paths below and run:
    cp ~/.claude/skills/impl-plan-codex-review/codex-{spawn,resume}.sh .claude/skills/impl-plan-codex-review/
    chmod +x .claude/skills/impl-plan-codex-review/codex-{spawn,resume}.sh

Codex profiles used:
  - codex-review-structure     → see structure-reviewer-prompt.md
  - codex-review-correctness   → see correctness-reviewer-prompt.md
  - codex-review-impl-generalist → see impl-generalist-reviewer-prompt.md
-->

# Implementation Plan Review with Codex Council

## Overview

Runs two specialized Codex review agents against an implementation plan in a council pattern with cooperative disagreement. The structure reviewer checks plan completeness and ordering. The correctness reviewer checks each step works. Claude orchestrates: both review in parallel, Claude triages findings (can agree or argue back), fix subagents handle edits, unresolved disagreements escalate to the user. Max 10 rounds, followed by a fresh generalist pass.

**Announce at start:** "Running Codex council review on the implementation plan (structure + correctness reviewers)."

**Prerequisites:**

- OpenAI Codex CLI installed (`npm install -g @openai/codex`)

## Preflight Check

```bash
which codex && echo "OK" || echo "MISSING: run npm install -g @openai/codex"
```

```bash
mkdir -p ~/.codex/sessions && touch ~/.codex/sessions/.write-test && rm ~/.codex/sessions/.write-test && echo "OK" || echo "MISSING: fix permissions on ~/.codex/"
```

If any check fails, inform user and stop.

## Setup

Create an isolated temp directory for this review session:

```bash
REVIEW_DIR=$(mktemp -d /tmp/codex-impl-review-XXXXXX)
echo "$REVIEW_DIR" > /tmp/.codex-impl-review-active
```

All output files go in `$REVIEW_DIR`.

## Session State

All session state is persisted to files inside `$REVIEW_DIR` so it survives context compaction.

**Saved automatically during execution:**

- `/tmp/.codex-impl-review-active` — pointer to current `REVIEW_DIR`
- `$REVIEW_DIR/struct-thread-id.txt` — structure reviewer thread ID
- `$REVIEW_DIR/correct-thread-id.txt` — correctness reviewer thread ID
- `$REVIEW_DIR/current-round.txt` — current round number
- `$REVIEW_DIR/plan-path.txt` — plan file path
- `$REVIEW_DIR/decision-log.md` — audit trail of every finding decision

**Recovery after context compaction:**

```bash
REVIEW_DIR=$(cat /tmp/.codex-impl-review-active)
STRUCT_THREAD_ID=$(cat $REVIEW_DIR/struct-thread-id.txt)
CORRECT_THREAD_ID=$(cat $REVIEW_DIR/correct-thread-id.txt)
CURRENT_ROUND=$(cat $REVIEW_DIR/current-round.txt)
PLAN_PATH=$(cat $REVIEW_DIR/plan-path.txt)
```

If context was compacted mid-review, recover state with the commands above, then resume from the current round.

## Review Loop

For each round N (max 10):

### Step 1: Run Both Reviewers in Parallel

Launch both Codex agents simultaneously (two parallel Bash tool calls). Set Bash timeout to 300000 (5 min) each.

**Structure reviewer (round 1 — spawn):**

```bash
~/.claude/skills/impl-plan-codex-review/codex-spawn.sh \
  codex-review-structure \
  $REVIEW_DIR/struct-review-r1.md \
  "Review the implementation plan at: {PLAN_PATH}" \
  > $REVIEW_DIR/struct-result-r1.json
```

**Correctness reviewer (round 1 — spawn):**

```bash
~/.claude/skills/impl-plan-codex-review/codex-spawn.sh \
  codex-review-correctness \
  $REVIEW_DIR/correct-review-r1.md \
  "Review the implementation plan at: {PLAN_PATH}. The project root is the current working directory. Check every file path by reading the actual files." \
  > $REVIEW_DIR/correct-result-r1.json
```

Read the JSON output files. Extract `threadId` from each and persist immediately:

```bash
STRUCT_THREAD_ID=$(jq -r '.threadId' $REVIEW_DIR/struct-result-r1.json)
CORRECT_THREAD_ID=$(jq -r '.threadId' $REVIEW_DIR/correct-result-r1.json)

echo "$STRUCT_THREAD_ID" > $REVIEW_DIR/struct-thread-id.txt
echo "$CORRECT_THREAD_ID" > $REVIEW_DIR/correct-thread-id.txt
echo "{PLAN_PATH}" > $REVIEW_DIR/plan-path.txt
echo "1" > $REVIEW_DIR/current-round.txt
```

**Step 1 is spawn-only (round 1).** Rounds 2+ start at Step 2 — the resume happens in Step 5 at the end of the previous round.

### Step 2: Read Both Reviews

The reviews are already embedded in the JSON output from Step 1. Extract them:

```bash
STRUCT_REVIEW=$(jq -r '.reviewerResponse' $REVIEW_DIR/struct-result-rN.json)
CORRECT_REVIEW=$(jq -r '.reviewerResponse' $REVIEW_DIR/correct-result-rN.json)
```

Alternatively, read from the markdown files written by the helper script:

- `$REVIEW_DIR/struct-review-rN.md`
- `$REVIEW_DIR/correct-review-rN.md`

### Step 3: Synthesize (Council Moderator)

1. **Consensus** — both flagged same problem → high confidence
2. **Unique** — one reviewer flagged → evaluate on merit
3. **Contradictions** — reviewers disagree → use judgment, explain
4. **Priority** — CRITICAL first, then IMPORTANT. Skip MINOR unless trivial.

### Step 4: Triage Each Finding

**CRITICAL RULES — read before triaging:**

- You MUST NOT skip the resume step when you disagree. "Not worth the resume" is NEVER a valid reason.
- You MUST NOT unilaterally dismiss a finding. Only the user can decide to skip a finding.
- You MUST log every decision to `$REVIEW_DIR/decision-log.md` before moving to the next finding.
- If you catch yourself thinking "I'll just note this and move on" — STOP. That means you're about to violate the protocol.

**Decision log format** — append this for EVERY CRITICAL/IMPORTANT finding:

```markdown
### Finding: <title>
- Source: <reviewer name>
- Severity: <CRITICAL/IMPORTANT>
- Claude's assessment: AGREE / DISAGREE
- Action taken: <fix subagent dispatched / resume sent>
- If DISAGREE → Codex decision: <WITHDRAW / MAINTAIN>
- If MAINTAIN → Escalated to user: YES
- Outcome: <fixed / withdrawn / user decided: fix|skip>
```

For each CRITICAL/IMPORTANT finding, one by one:

**If Claude AGREES:**

Dispatch a fix subagent immediately:

```
Task tool (general-purpose):
  description: "Fix <finding title> in plan"
  prompt: |
    You are fixing a specific issue in a plan document.

    Plan file: {PLAN_PATH}

    Issue: <the finding from Codex>
    Severity: <CRITICAL/IMPORTANT>
    Suggested fix: <from reviewer>

    Read the plan, apply the fix, keep changes minimal.
    Do NOT modify anything unrelated to this issue.

    Report what you changed.
```

Move to next finding after subagent reports.

**If Claude DISAGREES:**

Send counterargument via resume to the specific reviewer that flagged it:

```bash
~/.claude/skills/impl-plan-codex-review/codex-resume.sh \
  <profile> \
  <THREAD_ID> \
  $REVIEW_DIR/<reviewer>-counter-rN.md \
  "I disagree with your finding:

Issue: <the finding>
My counterargument: <why Claude thinks this is wrong or unnecessary>
Evidence: <code references, existing patterns, etc.>

Re-evaluate this specific finding. Respond with EXACTLY this format on the FIRST LINE:

DECISION: WITHDRAW
or
DECISION: MAINTAIN

Then explain your reasoning on subsequent lines." \
  > $REVIEW_DIR/<reviewer>-counter-rN.json
```

Read the JSON output and extract the reviewer response:

```bash
COUNTER_RESPONSE=$(jq -r '.reviewerResponse' $REVIEW_DIR/<reviewer>-counter-rN.json)
```

Parse the DECISION using multi-step strategy:

1. Check first line for `DECISION: WITHDRAW` or `DECISION: MAINTAIN`
2. Scan all lines for first occurrence
3. Semantic interpretation of full response
4. Fail-safe: treat as MAINTAIN

**For consensus findings** (both reviewers flagged same issue), resume **both** reviewers:

| Reviewer A | Reviewer B | Outcome |
|---|---|---|
| WITHDRAW | WITHDRAW | Resolved — skip fix |
| WITHDRAW | MAINTAIN | Escalate to user |
| MAINTAIN | WITHDRAW | Escalate to user |
| MAINTAIN | MAINTAIN | Escalate to user |

**For unique findings** (one reviewer), MAINTAIN → escalate to user.

**Escalation format:**

```
Disagreement on: <finding title>
Source: <reviewer name(s)>

Codex says: <the original finding + why it maintained>
Claude says: <the counterargument + reasoning>

Should I fix this?
```

**STOP after asking "Should I fix this?" — do NOT answer your own question. Wait for the user to respond.** User decides: fix → dispatch fix subagent. Skip → log reasoning, move on.

### Step 4b: Self-Verification Checkpoint

After triaging ALL findings, read `$REVIEW_DIR/decision-log.md` and verify:

1. Every CRITICAL/IMPORTANT finding has an entry
2. Every DISAGREE entry has "Action taken: resume sent" (not blank, not "skipped")
3. Every MAINTAIN entry has "Escalated to user: YES"
4. No findings were silently dismissed

If any entry is incomplete or missing, go back and complete the protocol for that finding NOW.

### Step 5: Resume Both Reviewers for Next Round

After all findings triaged and fixes applied, resume both reviewers in parallel with fix summary. This is the **only** resume point per round — Step 1 is spawn-only.

```bash
~/.claude/skills/impl-plan-codex-review/codex-resume.sh \
  codex-review-structure \
  {STRUCT_THREAD_ID} \
  $REVIEW_DIR/struct-review-rN.md \
  "I fixed the following issues:
{FIX_SUMMARY}

IMPORTANT: The document at {PLAN_PATH} has been modified since your last review. You MUST read the file again from disk — do NOT rely on your cached version from the previous round.

Perform a COMPLETE review of the entire document, not just a fix verification:
1. Verify your previous findings are properly resolved
2. Check for regressions or new issues introduced by the fixes
3. Re-examine EVERY section of the document for issues you may have missed in prior rounds — implicit assumptions, gaps, edge cases, interactions between sections
4. Review with the same rigor as your original review

Use the same output format as your original review. Report ALL findings, not just fix confirmations." \
  > $REVIEW_DIR/struct-result-rN.json
```

(Same pattern for correctness reviewer with `CORRECT_THREAD_ID`.)

Read the new reviews from the JSON output:

```bash
STRUCT_REVIEW=$(jq -r '.reviewerResponse' $REVIEW_DIR/struct-result-rN.json)
CORRECT_REVIEW=$(jq -r '.reviewerResponse' $REVIEW_DIR/correct-result-rN.json)
```

These are the input for the next round.

### Step 6: Evaluate

- Both PASS → proceed to "Fresh Eyes Pass"
- Round < 10 with issues → next round (back to Step 3 — synthesize the reviews from Step 5)
- Round 10 → present to user, then "Fresh Eyes Pass"

## Fresh Eyes Pass

```bash
~/.claude/skills/impl-plan-codex-review/codex-spawn.sh \
  codex-review-impl-generalist \
  $REVIEW_DIR/fresh-review.md \
  "Review the implementation plan at: {PLAN_PATH}
Review it holistically — structure, correctness, completeness, executability.
Focus on what a fresh reader would notice: inconsistencies, gaps, unclear steps, missing dependencies.

For each issue use this format:
- [CRITICAL|IMPORTANT|MINOR] <section>: <title>
  Why: <explanation>
  Fix: <suggestion>

End with:
## Summary
- Issues: N total (X critical, Y important, Z minor)
- Verdict: PASS | NEEDS FIXES
PASS = zero CRITICAL and zero IMPORTANT issues." \
  > $REVIEW_DIR/fresh-result.json
```

Read the fresh review:

```bash
FRESH_REVIEW=$(jq -r '.reviewerResponse' $REVIEW_DIR/fresh-result.json)
```

- No CRITICAL/IMPORTANT → done, proceed to "After Loop"
- If CRITICAL/IMPORTANT issues found → triage each one using the SAME protocol as Step 4:

**CRITICAL RULES apply here too:**

- You MUST NOT skip the resume step when you disagree.
- You MUST NOT unilaterally dismiss a finding.
- You MUST log every decision to `$REVIEW_DIR/decision-log.md`.
- Same escalation format, same decision log format, same self-verification as Step 4/4b.

Fix subagents handle any agreed fixes. **No second fresh pass** — single-shot review.

## After Loop

**CRITICAL: Unresolved disagreements gate.** Before presenting the summary, check `$REVIEW_DIR/decision-log.md` for any findings where Claude disagreed and the reviewer maintained (MAINTAIN). Each one MUST be individually escalated to the user using the escalation format. You MUST wait for the user's response on EACH disagreement before proceeding. Do NOT bundle them into the summary. Do NOT treat them as "already processed" or "stale". If the user has not explicitly said "fix" or "skip" for a disagreement, it is NOT resolved.

**After all disagreements are resolved by the user**, present the summary:

```
Codex council review complete after N round(s).

Structure review: [PASS | N remaining issues]
Correctness review: [PASS | N remaining issues]
Fresh eyes review: [PASS | N remaining issues]

Changes made:
- [all fixes across all rounds]

User decisions on disagreements:
- [each disagreement + user's fix/skip decision]

The reviewed plan is at: {PLAN_PATH}
```

Cleanup: `rm -rf $REVIEW_DIR`

## Placeholders

- `{PLAN_PATH}` — path to the implementation plan file
- `{STRUCT_THREAD_ID}` — thread_id from structure reviewer
- `{CORRECT_THREAD_ID}` — thread_id from correctness reviewer
- `{FIX_SUMMARY}` — bullet list of fixes from current round
