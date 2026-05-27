# Self-Learning Overview

This directory enables agents to improve repo-local knowledge after every
implementation iteration without hidden memory or uncontrolled drift.

## Principles

1. **Documentation-only updates.** Agents never modify production code as a
   learning action. Only files under `docs/ai-knowledge/`, `docs/features/`,
   and `.claude/agents/` may be updated through the learning pipeline.

2. **Explicit proposals.** All learning updates are written to
   `proposed-updates.md` before any file is changed. The `knowledge-curator`
   agent reviews each proposal.

3. **Auditable history.** Every accepted update is logged in `iteration-log.md`.
   Every rejected update is logged in `rejected-updates.md` with a reason.

4. **Source-of-truth authority.** The authoritative record of repo state is
   always the source code. Learning updates must cite the source file and line
   that justifies the change.

## Permitted update targets

| Target | Who may propose | Who approves |
|--------|----------------|--------------|
| `docs/ai-knowledge/services/*.md` | Any implementer or reviewer | knowledge-curator |
| `docs/ai-knowledge/communication/*.md` | communication-flow-mapper, service-contract-reviewer | knowledge-curator |
| `docs/ai-knowledge/frontend/*.md` | typescript-frontend-implementer, frontend-ui-kit-reviewer | knowledge-curator |
| `docs/ai-knowledge/ui-kit/*.md` | ui-kit-cartographer, frontend-ui-kit-reviewer | knowledge-curator |
| `docs/ai-knowledge/observability/*.md` | observability-mapper, observability-reviewer | knowledge-curator |
| `docs/ai-knowledge/features/*.md` (local) | feature-documenter, any domain-expert | knowledge-curator |
| `docs/features/*.md` | feature-documenter, any domain-expert | knowledge-curator |
| `docs/ai-knowledge/services/service-inventory.json` | service-boundary-mapper | knowledge-curator + human review |
| `.claude/agents/*.md` | sdd-orchestrator only | human review required |

## Prohibited updates

- Production code (`src/**`)
- Test files (`test/**`)
- Proto contracts (`pb/**`)
- Infrastructure config (`docker-compose*.yml`, `kubernetes/**`, `.env*`)
- Hook scripts (`.claude/hooks/**`)
- Gate scripts (`scripts/ai/**`)

## Workflow

```
implementer completes task
    ↓
subagent-stop-quality-gate.py runs gates
    ↓
reviewer agents return findings
    ↓
sdd-orchestrator identifies knowledge gaps
    ↓
knowledge-curator writes proposed-updates.md entry
    ↓
knowledge-curator applies accepted updates
    ↓
knowledge-curator appends to iteration-log.md
    ↓
rejected updates → rejected-updates.md
```
