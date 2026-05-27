---
description: Run the full project intelligence setup: extract docs, generate agents, discover gates, setup validation, and enable self-learning.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Bootstrap

Goal:
Prepare this repository for SDD by teaching the harness the codebase.

Do not modify production code.

Run these phases in order:

1. /project-extract-docs
2. /project-generate-agents
3. /project-setup-quality-gates
4. /project-enable-self-learning

Expected outputs:
- docs/ai-knowledge/**/*
- docs/features/**/*
- specs/bootstrap-report.md
- .claude/agents/domain-*-expert.md
- .claude/agents/*-implementer.md
- .claude/agents/*-reviewer.md
- scripts/ai/review-router.py
- scripts/ai/gate-router.sh
- .sdd/evidence/bootstrap-complete

Completion rule:
Do not finish until bootstrap report exists and the harness can explain:
- what services exist,
- how they communicate,
- what features - what features - what features - what features - whats were generated,
- how validation runs after implementer stop.
