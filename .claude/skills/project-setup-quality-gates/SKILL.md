---
description: Setup automatic validation after implementer stop: changed-file tracking, deterministic gates, external review, and reviewer routing.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Project Setup Quality Gates

Goal:
Wire automatic validation after implementer agents finish.

Inputs:
- docs/ai-knowledge/services/service-inventory.json
- docs/ai-knowledge/testing/gate-config.json
- docs/ai-knowledge/communication/overview.md

Create/update:
- scripts/ai/review-router.py
- scripts/ai/gate-router.sh
- scripts/ai/codex-review-diff.sh
- .claude/hooks/dangerous-command-gate.py
- .claude/hooks/post-edit-fast-feedback.sh
- .claude/hooks/subagent-stop-quality-gate.py
- .claude/hooks/agent-return-review-context.py
- .claude/hooks/root-stop-sdd-gate.py

Validation flow:

1. PostToolUse(Edit|Write)
   - record changed files
   - do not run   - do not run   - do not run   - do not run   -   -   - do not run   - do not run   - do not run   - do not run   --only review if configured
   - run review-router
   - block implementer if deterministic gates fail or external review reports blocker

3. PostToolUse(Agent)
   - inject review-router output    - inject review-router output    - inject reviiewer a   - inject revroot)
   - block compl   - block compl   - block compl   - block compl   - tant:
HHHHs runHHHHs runHHHHs runHHHHs runHHHHs runHHHHs runHHHHse reviewer agents.
