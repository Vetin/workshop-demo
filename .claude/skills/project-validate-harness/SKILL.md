---
description: Validate the generated project intelligence harness before SDD pipeline setup.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Validate Harness

Goal:
Self-review the generated docs, agents, hooks, validation categories, and learning policy.

Do not modify production code.

Run:
1. harness-self-reviewer
2. docs-consistency-reviewer
3. project-rules-reviewer
4. knowledge-curator

Check:
- every known service has docs,
- every known service has a domain expert,
- every implementation platform has an implementer,
- every major validation category has a reviewer,
- every reviewer is read-only,
- every implementer has bounded scope,
- validation gates are documented,
- hooks are wired,
- self-learning has review controls,
- bootstrap evidence exists.

Create:
- specs/bootstrap-report.md
- .sdd/evidence/bootstrap-complete.md- .sdd/evidence/bootstrap-complete.md- .sdd/evi- fix it,
- rerun self-review.
