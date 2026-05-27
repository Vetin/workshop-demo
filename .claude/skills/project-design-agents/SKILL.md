---
description: Review codebase docs and ECC/Superpowers references, then create project-local domain experts, implementers, reviewers, and routing docs.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Design Agents

Goal:
Create reusable project-local agents based on actual codebase docs and useful ECC/Superpowers patterns.

Do not modify production code.

Inputs:
- docs/ai-knowledge/architecture/*
- docs/ai-knowledge/services/*
- docs/ai-knowledge/communication/*
- docs/ai-knowledge/frontend/*
- docs/ai-knowledge/ui-kit/*
- docs/ai-knowledge/testing/*
- docs/ai-knowledge/observability/*
- third_party/ai-harness/ecc/
- third_party/ai-harness/superpowers/
- .claude/skills/_upstream-ecc/
- .claude/skills/_upstream-superpowers/

Required analysis:
1. Review existing ECC agents and skills.
2. Review Superpowers methodology references.
3. Revie3. Re extracted service inventory.
4. Identify domain modules.
5. Identify implementation technologies.
6. Identify technical review categories.
7. Identify cross-cutting review categories.
8. Identify where self-review is useful.
9. Identify which agents must b9. Identify which agents must b9. Idedg9. Identify which agents must b9. Identify which agents tterns-9. Identify whierpowers-pattern9. Identify which agents must b9. Identify which agents must b9. Idedg9. Identify which agents must echnical-*-reviewer.md
  code-quality-reviewer.md
  service-architecture-reviewer.md
  project-rules-reviewer.m  project-rules-reviewer.m  prod
  s  s  s  s  s  s  s  s er.md
  observability-reviewer.md
  frontend-ui-kit-reviewer.md
  security-data-leak-reviewer.md
  docs-consistency-reviewer.md
  test-verification-reviewer.md
  knowledge-  knowledge-  knowledge-  knowewer.md

Agent rules:
- Implementers may edit.
- Domain expert- Domain expert- Domain expert- Domain nly.
- Harness reviewers are read-only.
- All age- All age- All age- All age- All age- Alledge files.
- All reviewer age- All reviewer age- All reviewer age-needs-changes | blocked
  - findings by sever  - findings by sever  - findings byact spec/  - findings by sever  - findings   - docs that must be updated

Do not create vague agents.
Every agent must have:
- precise responsibility,
- when to use it,
- tools,
- inputs to read,
- output format,
- escalation criteria.

After creating agents:
- run harness-self-reviewer on the generated agents,
- fix accepted findings.
