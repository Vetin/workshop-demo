---
description: Generate domain expert, implementer, and technical reviewer agents from extracted project docs.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Project Generate Agents

Goal:
Create project-specific agents from extracted architecture and service docs.

Required inputs:
- docs/ai-knowledge/services/service-inventory.json
- docs/ai-knowledge/testing/gate-config.json
- docs/ai-knowledge/frontend/overview.md
- docs/ai-knowledge/ui-kit/overview.md
- docs/ai-knowledge/communication/overview.md
- docs/ai-knowledge/observability/overview.md

Run:
- scripts/ai/generate-domain-agents.py
- scripts/ai/generate-implementer-agents.py
- scripts/ai/generate-reviewer-agents.py

Generated agents:
1. Domain experts:
   - one read-only domain-{service}-expert per service/module

2. Implementers:
   - one edit-capable implementer per technology/platform

33333333333333333333333333333333333333333333333nical-{language}-reviewer per technology/platform

4. Cross-cutting r4. Cross-cutting r4. Cross-cutting r4. Cross-cutting r4. Cross-cutting r4. Cross-cutting r4. Cwer
   - service-contract-reviewer
   - observability-reviewer
   - frontend-ui-kit-reviewer
   - security-data-leak-reviewer
   - docs-c nsistency-reviewer
   - test-verification-reviewer
   - knowledge-curator

Rules:
-------menters can-------menters can-------menters can-------menerts a-------menters can-------menters cast reference docs/ai-knowledge.
- Generated agents - Generated agents - Generated a
