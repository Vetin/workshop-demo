---
description: Audit and refine project-local Claude Code agents. Makes agents domain-specific, attaches language/runtime knowledge, reuses ECC/Superpowers patterns, archives irrelevant legacy agents, and updates routing docs.
argument-hint: '[optional focus area: all|implementers|reviewers|domain-experts|legacy|language]'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Refine Agents

Goal:
Improve all active agents in `.claude/agents/` so they are specific to this repository, this architecture, this language mix, and this SDD harness.

This skill runs after `/project-bootstrap` and before `/sdd-setup-pipeline`.

Do not modify production code.

## Inputs

Read:

- `.claude/agents/*.md`
- `docs/ai-knowledge/architecture/*`
- `docs/ai-knowledge/services/*`
- `docs/ai-knowledge/communication/*`
- `docs/ai-knowledge/frontend/*`
- `docs/ai-knowledge/ui-kit/*`
- `docs/ai-knowledge/testing/*`
- `docs/ai-knowledge/observability/*`
- `docs/ai-knowledge/validation/*`
- `docs/ai-knowledge/agents/*`
- `.claude/skills/_upstream-ecc/*`
- `.claude/skills/_upstream-superpowers/*`
- `third_party/ai-harness/ecc/`
- `third_party/ai-harness/superpowers/`

Optional focus:

$ARGUMENTS

If no focus is given, refine all active agents.

## Outputs

Create or update:

```text
docs/ai-knowledge/agents/
  agent-catalog.md
  agent-routing.md
  agent-refinement-report.md
  agent-design-decisions.md
  legacy-agents.md

docs/ai-knowledge/agents/legacy/
  {agent-name}.md

docs/ai-knowledge/languages/
  overview.md
  typescript-nextjs.md
  go.md
  python.md
  dotnet.md
  java-kotlin.md
  nodejs.md
  rust.md
  ruby.md
  php.md
  cpp.md
  infra-config.md
```

Update active agents in:

.claude/agents/\*.md

Only if the agent remains relevant.

Main process

1. Inventory active agents

List every Markdown file under:

.claude/agents/

For each agent, record:

file path
name
description
tools
model
whether it can edit files
whether it is an implementer, reviewer, domain expert, orchestrator, bootstrap agent, or legacy candidate
referenced docs/ai-knowledge files
service/domain coverage
language/runtime coverage
duplicate or overlapping agents
missing responsibilities
unsafe permissions

Write the inventory to:

docs/ai-knowledge/agents/agent-catalog.md 2. Build language/runtime knowledge

Inspect the codebase docs and create language-specific knowledge files under:

docs/ai-knowledge/languages/

Each language knowledge file must include:

when this language appears in the repo
service paths using it
build/test commands
style and architecture patterns
common failure modes
generated-code rules
telemetry/instrumentation patterns
recommended implementer behavior
recommended reviewer checks

Do not invent rules. Mark unknowns explicitly.

3. Identify legacy agents

An agent is legacy if it is:

not mapped to any current service, feature, language, or validation category
duplicated by a better local agent
copied from ECC without project localization
too vague to route reliably
unsafe because it can edit files while acting as a reviewer
incompatible with the current SDD workflow
no longer used by sdd-orchestrator, validation docs, or pipeline docs

For each legacy agent:

Copy its original content to:
docs/ai-knowledge/agents/legacy/{agent-name}.md
Add a legacy record with:

# Legacy Agent: {agent-name}

## Original path

.claude/agents/{agent-name}.md

## Reason archived

## Replacement agent

## Migration notes

## Date

## Reviewer

Remove it from active .claude/agents/ only after documenting the reason.

Never silently delete an agent.

4. Refine domain expert agents

For each domain-\*-expert agent:

Make it service-specific.

It must include:

exact service/module path
exact service responsibility
inbound communication
outbound communication
relevant contracts
relevant feature docs
relevant test commands
relevant observability docs
when to use
what it must review
what it must not review
read-only tools only
structured output

Domain expert agents must be read-only.

Required output format:

verdict: pass | needs-changes | blocked

findings:

- severity: blocker | major | minor | suggestion
  file:
  spec_or_doc:
  issue:
  evidence:
  required_fix:

docs_to_update:

- path:
  reason:

unknowns:

- question:
  blocking: true | false

5. Refine implementer agents

For each \*-implementer agent:

Make it technology-specific and repo-specific.

It must include:

assigned language/runtime
assigned service/module paths
docs to read first
language knowledge file to read
test commands to use
generated-code rules
contract-change rules
telemetry rules
evidence requirements
stop behavior

Implementer agents may edit files, but only inside their assigned task.

Each implementer must say:

Do not claim task completion yourself.
When you stop, SubagentStop hooks will run deterministic gates.
The root orchestrator will then run reviewer agents. 6. Refine reviewer agents

For each reviewer agent:

Make it read-only and category-specific.

Reviewer categories should include:

code-quality-reviewer
service-architecture-reviewer
project-rules-reviewer
distributed-flow-reviewer
service-contract-reviewer
observability-reviewer
frontend-ui-kit-reviewer
security-data-leak-reviewer
docs-consistency-reviewer
test-verification-reviewer
knowledge-curator
harness-self-reviewer
technical-{language}-reviewer

Every reviewer must include:

when to use
docs to read
exact review checklist
non-goals
output format
escalation criteria

Reviewers must not edit files.

7. Apply ECC and Superpowers patterns carefully

Use ECC and Superpowers as inspiration only.

From ECC, reuse patterns such as:

code reviewer structure
security reviewer structure
doc updater structure
e2e/browser QA structure
context budget practices
coding standards practices

From Superpowers, reuse patterns such as:

plan before implementation
TDD loop
subagent-driven implementation
spec compliance review before code-quality review
verification before completion
no stopping between tasks unless blocked, ambiguous, or complete

Do not copy upstream agents blindly.

For every reused pattern, record it in:

docs/ai-knowledge/agents/agent-design-decisions.md 8. Update agent routing docs

Create or update:

docs/ai-knowledge/agents/agent-routing.md

It must answer:

Which implementer handles each language/runtime?
Which domain expert handles each service?
Which reviewers always run?
Which reviewers run conditionally?
Which agents are forbidden from editing?
Which agents are used only during bootstrap?
Which agents are legacy and replaced? 9. Update validation docs

Create or update:

docs/ai-knowledge/validation/reviewer-routing.md
docs/ai-knowledge/validation/stop-hook-policy.md
docs/ai-knowledge/validation/validation-categories.md

Ensure validation categories include:

code quality
service architecture
project rules
domain behavior
technical correctness by language/runtime
distributed flow
service contract compatibility
observability
security/data leakage
frontend/UI-kit consistency
testing/verification evidence
documentation consistency
knowledge update quality 10. Self-review the refined harness

After updating agents, run:

harness-self-reviewer
project-rules-reviewer
docs-consistency-reviewer
knowledge-curator

Fix accepted findings.

Create:

docs/ai-knowledge/agents/agent-refinement-report.md
.sdd/evidence/agent-refinement-complete.md
Safety rules

Do not modify production code.

Do not silently delete active agents.

Do not give edit tools to reviewers.

Do not make all agents read every doc. Use progressive loading:

relevant overview.md
relevant detail.md only when needed
exact service docs only for touched services
exact language docs only for touched language/runtime

Do not create vague agents.

Do not create agents that duplicate sdd-orchestrator.

Do not create agents for languages, services, or features not found in the repo unless clearly marked as future/planned and not active.

Completion checklist

Before finishing, verify:

every active agent has a precise role
every active agent has a clear description
every reviewer is read-only
every implementer is scoped
every domain expert maps to a real service/module
every implementer maps to a real language/runtime
every technical reviewer maps to a real language/runtime
every active agent references relevant docs/ai-knowledge
every legacy agent is archived with reason
agent routing docs are updated
validation routing docs are updated
self-review passed or unresolved findings are listed
