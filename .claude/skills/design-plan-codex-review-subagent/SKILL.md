---
name: design-plan-codex-review-subagent
description: Reviews a design plan using a Codex council — architecture and feasibility reviewers in a cooperative disagreement loop, followed by a fresh eyes pass. Codex sessions are managed by the codex-reviewer subagent; thread IDs flow through agent responses enabling resume across rounds.
---

# Design Plan Review with Codex Council

**Announce at start:** "Running Codex council review on the design plan (architecture + feasibility reviewers)."

**Requires:** `codex` CLI installed, `codex-reviewer` agent (`.claude/agents/codex-reviewer.md`)

## Preflight

```bash
which codex && echo "OK" || echo "MISSING: run npm install -g @openai/codex"
```

Stop if preflight fails.

## Round Loop (max 10 rounds)

### Round 1 — Spawn both reviewers in parallel

Send both Agent calls in the **same message** so they run concurrently.

```
Agent(subagent_type: "codex-reviewer", description: "Architecture reviewer — round 1", prompt: """
profile:   codex-review-architecture
plan_path: {PLAN_PATH}
prompt:    Review the design plan at: {PLAN_PATH}
thread_id:
""")

Agent(subagent_type: "codex-reviewer", description: "Feasibility reviewer — round 1", prompt: """
profile:   codex-review-feasibility
plan_path: {PLAN_PATH}
prompt:    Review the design plan at: {PLAN_PATH}. The project root is the current working directory.
thread_id:
""")
```

Each response format:
```
THREAD_ID: <id>
---
<review text>
```

Parse both responses. Track `ARCH_THREAD_ID`, `FEAS_THREAD_ID`, and both reviews in your context.

### Rounds 2+ — Resume both reviewers in parallel (Step 5)

After fixes are applied, resume both in the **same message**:

```
Agent(subagent_type: "codex-reviewer", description: "Architecture reviewer — resume round N", prompt: """
profile:   codex-review-architecture
plan_path: {PLAN_PATH}
thread_id: {ARCH_THREAD_ID}
prompt:    I fixed the following issues:
{FIX_SUMMARY}

The document at {PLAN_PATH} has been updated. Read it again from disk.

Perform a COMPLETE review — verify fixes, check for regressions, re-examine every section.
Use the same output format as your original review.
""")

Agent(subagent_type: "codex-reviewer", description: "Feasibility reviewer — resume round N", prompt: """
profile:   codex-review-feasibility
plan_path: {PLAN_PATH}
thread_id: {FEAS_THREAD_ID}
prompt:    [same instructions]
""")
```

Resume responses contain only review text (no `THREAD_ID:` line — thread IDs don't change on resume).

## Synthesize (Council Moderator)

For each round's two reviews:

1. **Consensus** — both flagged same problem → high confidence
2. **Unique** — one reviewer flagged → evaluate on merit
3. **Contradictions** — reviewers disagree → use judgment, explain
4. **Priority** — CRITICAL first, then IMPORTANT. Skip MINOR unless trivial.

## Triage Each Finding

**CRITICAL RULES:**
- Never skip the resume/counterargument step when you disagree.
- Never unilaterally dismiss a finding — only the user can do that.
- Log every CRITICAL/IMPORTANT decision before moving to the next finding.

**Decision log format** (append to a running log in your context):

```
Finding: <title> | Source: <reviewer> | Severity: CRITICAL/IMPORTANT
Claude: AGREE → fix subagent dispatched
Claude: DISAGREE → resume sent → Codex: WITHDRAW/MAINTAIN → [fixed | escalated to user]
```

### If Claude AGREES → dispatch fix subagent:

```
Agent(description: "Fix <title>", prompt: """
Fix this issue in the plan at {PLAN_PATH}:

Issue: <finding>
Severity: <CRITICAL/IMPORTANT>
Fix: <suggestion>

Keep changes minimal. Report what changed.
""")
```

### If Claude DISAGREES → send targeted resume to that reviewer:

```
Agent(subagent_type: "codex-reviewer", description: "Counterargument — <reviewer>", prompt: """
profile:   <profile>
plan_path: {PLAN_PATH}
thread_id: {THREAD_ID}
prompt:    I disagree with your finding:

Issue: <finding>
My counterargument: <reasoning>
Evidence: <references>

Respond with EXACTLY this on the FIRST LINE:
DECISION: WITHDRAW
or
DECISION: MAINTAIN
""")
```

Parse `DECISION:` from the first line. Fail-safe: treat as MAINTAIN.

**Consensus findings** — resume both reviewers:

| A | B | Outcome |
|---|---|---------|
| WITHDRAW | WITHDRAW | resolved |
| any MAINTAIN | any MAINTAIN | escalate to user |

**Unique findings** — MAINTAIN → escalate to user.

**Escalation:**
```
Disagreement on: <title>
Codex says: <finding + reasoning>
Claude says: <counterargument>
Should I fix this?
```

**STOP and wait.** Do not answer your own question.

### Self-verification checkpoint

After triaging all findings, verify your decision log:
- Every CRITICAL/IMPORTANT finding has an entry
- Every DISAGREE has a resume action recorded
- Every MAINTAIN has "escalated to user"
- Nothing silently dismissed

## After Each Round

- Both PASS → Fresh Eyes Pass
- Issues remain, round < 10 → resume both reviewers (Step 5), then re-synthesize
- Round 10 → present all remaining concerns to user, apply any requested fixes, then Fresh Eyes Pass

## Fresh Eyes Pass

```
Agent(subagent_type: "codex-reviewer", description: "Generalist fresh eyes", prompt: """
profile:   codex-review-design-generalist
plan_path: {PLAN_PATH}
thread_id:
prompt:    Review the design plan at: {PLAN_PATH}

Review holistically — architecture, feasibility, coherence, completeness.
Focus on what a fresh reader notices: gaps, inconsistencies, unstated assumptions.

Format each issue:
- [CRITICAL|IMPORTANT|MINOR] <section>: <title>
  Why: <explanation>
  Fix: <suggestion>

End with:
## Summary
- Issues: N total (X critical, Y important, Z minor)
- Verdict: PASS | NEEDS FIXES
""")
```

Triage the fresh review using the same protocol (AGREE/DISAGREE/ESCALATE). No second fresh pass.

## Completion Gate

Before the final summary: check your decision log for any MAINTAIN findings not yet resolved by the user. Escalate each one individually. Wait for explicit user response (fix or skip) before proceeding.

**Final summary:**
```
Codex council review complete — N round(s).

Architecture: PASS | N issues
Feasibility:  PASS | N issues
Fresh eyes:   PASS | N issues

Fixes applied: [list]
User decisions: [list]

Reviewed plan: {PLAN_PATH}
```
