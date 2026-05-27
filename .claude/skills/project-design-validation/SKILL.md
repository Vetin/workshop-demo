---
description: Design validation categories, quality gates, hook behavior, and review routing based on extracted project docs and generated agents.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Design Validation

Goal:
Create validation after implementer stop.

Inputs:
- docs/ai-knowledge/testing/*
- docs/ai-knowledge/services/*
- docs/ai-knowledge/communication/*
- docs/ai-knowledge/observability/*
- docs/ai-knowledge/agents/*
- .claude/agents/*

Create:

docs/ai-knowledge/validation/
  overview.md
  gates.md
  validation-categories.md
  stop-hook-policy.md
  reviewer-routing.md
  evidence-format.md

scripts/ai/
  run-gate.sh
  codex-review-diff.sh
  changed-files.sh
  write-evidence.sh

.claude/hooks/
  dangerous-command-gate.py
  post-edit-fast-feedback.sh
  subagent-stop-quality-gate.py
  agent-return-review-context.py
  root  root  root  root  root  root  root  root  rootclu  root  root  root  root  root  root  root  root  rootclu  roool  wi  root  root  root  root  root  root  root  root  rootclu  root  root  root  root  root  root  root  root  rootclu  roool  wi  root  root  root d   root  root  root  root  root  roo dat  root  root  root  root  root  root  root  root  rootcnd verification evidence
12. Documentation 12. Documentation 12. Documentation 12. ty
12. Doat12. Doat12. Doat12. Doat1Edit|12. Doat12. Doat12. Doat12. Dle12. Doat12. Doat12. Doat12. Doat1tte12. Doat12. Doat12. Doat12. Doatexpe12. Doat12. Doat12. Doat12.en12. Doat12. Doters)
1  - run 1  - run 1  - run 1  - run 1s/1  - run 1  /v1lidation/g1  - run 1  - run 1  - ruea1  - run 1  - run 1 f 1  - run 1  - run 1 e 1  - run 1  - dd/gates1  - run 1p}1  - run rite 1  - run 1  - run 1  estion to .sdd/evidence/review-router.latest.md,
   - block if deterministic gates fail or external review reports blocker.

3. PostToolUse(Agent)
   - remind orchestrator to spawn reviewer agents listed in .sdd/evidence/review-router.latest.md.

4. Stop(root)
   - block final completion claims when required evidence is missing.

Important:
Hooks should not replace orchestrator judgment.
Hooks enforce deterministic checks and evidence.
The orchestrator runs Claude reviewer agents.
