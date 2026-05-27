---
description: Enable controlled repo-local self-learning by creating knowledge-update rules, learning logs, and docs review gates.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Enable Self-Learning

Goal:
Allow agents to improve repo-local knowledge after every iteration without hidden memory or uncontrolled drift.

Create:
- docs/ai-knowledge/learning/overview.md
- docs/ai-knowledge/learning/detail.md
- docs/ai-knowledge/learning/iteration-log.md
- docs/ai-knowledge/learning/proposed-updates.md
- docs/ai-knowledge/learning/rejected-updates.md

Rules:
1. Learning updates are documentation updates only.
2. Agents may propose updates to:
   - docs/ai-knowledge/services/*.md
   - docs/ai-knowledge/communication/*.md
   - docs/ai-knowledge/frontend/*.md
   - docs/ai-knowledge/ui-kit/*.md
   - docs/ai-knowledge/testing/*.md
                                                      atu                                                      atu         - .cl                                                      atu                                                      atu         - .clsi                                urator

5. Every rejected learning update must record:
   - proposal
   - reason rejected
   - reviewer
   - date
