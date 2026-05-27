# SDD Pipeline Setup Evidence

Date: 2026-05-27
Run: sdd-setup-pipeline

## Files created or rewritten

### Pipeline docs
- .sdd/pipeline.md — complete rewrite (was corrupted)
- .sdd/pipeline.json — complete rewrite, version bumped to 2 (was corrupted)

### SDD skill files (all rewritten — originals had encoding corruption)
- .claude/skills/sdd-start/SKILL.md
- .claude/skills/sdd-review-design/SKILL.md
- .claude/skills/sdd-plan/SKILL.md
- .claude/skills/sdd-review-plan/SKILL.md
- .claude/skills/sdd-execute/SKILL.md
- .claude/skills/sdd-verify/SKILL.md
- .claude/skills/sdd-finalize/SKILL.md

### New agent files (created — were missing)
- .claude/agents/spec-compliance-reviewer.md (blocker F-07 fix)
- .claude/agents/distributed-flow-reviewer.md (blocker F-08 fix)

### Feature templates (updated)
- docs/features/_template/changes/_template/tasks/task-template.md
  — added files_likely_touched to frontmatter
- docs/features/_template/changes/_template/tasks/task-evidence-template.md
  — added observability, security, test-verification review sections

### Validation docs (all rewritten — originals had encoding corruption)
- docs/ai-knowledge/validation/sdd-review-loop.md
- docs/ai-knowledge/validation/sdd-agent-routing.md
  — added 11 missing domain expert routing entries
- docs/ai-knowledge/validation/sdd-evidence-format.md

## Harness self-review findings and resolutions

| ID | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| F-01 | major | reviewOrder in pipeline.json missing conditional reviewers | Fixed: inserted conditional slots with labels |
| F-02 | minor | security-data-leak-reviewer in both always and conditional | Fixed: removed from conditionalReviewers |
| F-03 | minor | frontend-proxy missing from pipeline.md implementer table | Fixed: added to infra-otel-implementer row |
| F-04 | major | test-verification-reviewer position mismatch in pipeline.md | Fixed: moved to position 6, before conditional reviewers |
| F-05 | minor | finalization reviewer order wrong in sdd-finalize | Fixed: knowledge-curator now runs before docs-consistency-reviewer |
| F-06 | major | 9 domain expert routing entries missing from sdd-agent-routing.md | Fixed: added all 11 missing rows |
| F-07 | blocker | spec-compliance-reviewer.md agent missing | Fixed: created agent file |
| F-08 | blocker | distributed-flow-reviewer.md agent missing | Fixed: created agent file |
| F-09 | major | Broken upstream paths in sdd-execute/SKILL.md | Fixed: corrected to skill-local paths |
| F-10 | major | Broken upstream path in sdd-plan/SKILL.md | Fixed: corrected to skill-local path |
| F-11 | major | Broken upstream path in sdd-verify/SKILL.md | Fixed: corrected to skill-local path |
| F-12 | minor | Missing finalVerificationRules in pipeline.json | Fixed: added structured key |
| F-13 | minor | technical-{language}-reviewer not in alwaysRunReviewers | Fixed: added with per-language note |
| F-17 | minor | files_likely_touched missing from task-template frontmatter | Fixed: added field |
| F-21 | minor | 02-design-review.md missing from sdd-review-plan inputs | Fixed: added to required input list |
| F-22 | major | Flat legacy feature files not addressed in sdd-start | Fixed: added migration note to step 2 |

## Status

All findings resolved. Pipeline is consistent and ready for use.
