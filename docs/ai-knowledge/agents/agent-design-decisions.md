# Agent Design Decisions

Why the SDD harness is structured the way it is, and which external patterns it draws from.

Last updated: 2026-05-27

---

## Patterns from Superpowers

The following patterns are drawn from the Superpowers methodology and applied throughout this harness:

### Plan-before-implementation
All feature work goes through three gates before any code is written:
1. Design doc (brainstorming output) — captures intent, constraints, affected services
2. Implementation plan (writing-plans output) — step-by-step task list with reviewer assignments
3. Implementation — agents execute the plan, one service at a time

This prevents scope creep and ensures each implementer agent has a bounded, unambiguous task.

### TDD loop for bugs
When a bug is reported, a regression test is written first (or identified in `test/tracetesting/`) before the implementer is dispatched. This ensures the fix can be verified locally and that the same bug cannot silently reappear.

### Subagent-driven implementation
Each implementer is scoped to exactly one language/service set. This matches the Superpowers subagent-driven-development pattern: independent tasks dispatched to independent agents, no shared state. The orchestrator coordinates sequencing when cross-service changes are needed.

### Spec compliance review before code-quality review
Reviewers run in a fixed order: observability-reviewer first (spec compliance — is the OTel instrumentation correct?), then technical-{language}-reviewer (code quality — is the implementation idiomatic?). This order prevents code-quality findings from being accepted while a spec violation still exists.

### No stopping between tasks unless blocked, ambiguous, or complete
Implementer agents do not stop to check in mid-task. They stop when:
- The task is complete (normal completion)
- They are blocked (missing information, conflicting requirements)
- They hit scope ambiguity (the change would affect a service outside their assigned paths)

### Verification before completion
Implementer agents must leave evidence in `.sdd/evidence/` before stopping. The SubagentStop hook validates that evidence exists. An agent claiming completion without local verification evidence is treated as incomplete.

---

## Patterns from ECC

The following patterns are drawn from the ECC (Enterprise Claude Code) methodology:

### Code reviewer structure organized by language
Technical reviewers are 1:1 with implementers: one reviewer per language/runtime. This mirrors the ECC pattern of pairing each implementer with a language-specific reviewer. Cross-cutting concerns (OTel, security, service contracts) are handled by separate specialized reviewers that run on top of the language reviewers.

### Security reviewer focused on telemetry data
The ECC security reviewer pattern is adapted here specifically for observability: `security-data-leak-reviewer` focuses on PII in span attributes and log bodies rather than general application security. This is the highest-risk security surface in an OTel demo app (traces and logs may be sent to multiple backends).

### Doc updater structure: curator + consistency pair
The ECC doc-updater pattern becomes a two-agent pair here:
- `knowledge-curator` — writes new docs/ai-knowledge/ entries and updates existing ones after implementation
- `docs-consistency-reviewer` — verifies the updated docs accurately match the code reality

The split ensures that the agent doing the writing (knowledge-curator) is not also the agent verifying accuracy (docs-consistency-reviewer).

### Context budget practices: progressive loading in domain experts
Domain experts use progressive loading: they read only the docs and code files relevant to their assigned service, not the entire codebase. This mirrors the ECC pattern of scoping agent context to the minimum needed to answer the question. Each domain expert loads its service's source path, proto definitions for that service, and its section of the communication flow map.

---

## Local Decisions for This Repo

Design decisions specific to the OpenTelemetry Demo that are not directly derived from Superpowers or ECC:

### Dual technical reviewer arbitration
When both a `technical-{language}-reviewer` and a specialized reviewer (e.g., `observability-reviewer`) find conflicting issues with the same code, both findings are reported independently to the orchestrator. The orchestrator arbitrates: if findings conflict, it favors the specialized reviewer finding (observability/security/contract) over the language-quality finding, unless the language finding reveals a correctness bug.

### OTel as a first-class review dimension
`observability-reviewer` always runs after any service code change — not just when OTel code changes. This is because any change to a service can inadvertently break telemetry (removing a span, changing a span name, altering propagation). Every service in this repo is an OTel teaching example, so telemetry correctness is a first-class concern.

### Single proto file rule
`pb/demo.proto` is the single source of truth for all gRPC contracts across all services. No service maintains its own separate proto file. `service-contract-reviewer` runs automatically on any change to `pb/demo.proto` or any generated stub file (`.pb.go`, `_pb2.py`, `*_grpc.rb`, etc.) to verify that all language implementations stay in sync.

### Harness corruption recovery: concurrent bootstrap writes
During the `project-generate-agents` run on 2026-05-27, concurrent writes to the same agent file paths corrupted two agent files:
- `sdd-orchestrator.md` — content was truncated/overwritten
- `service-boundary-mapper.md` — content was truncated/overwritten

Additionally, three empty non-markdown artifact files were created in `.claude/agents/`:
- `com:` — likely from a truncated write to `communication-flow-mapper.md` or `com:`
- `communication-flow-macat` — truncated filename from `communication-flow-mapper.md`
- `cper` — origin unclear, empty file

**Root cause:** `project-generate-agents` dispatched multiple bootstrap agents in parallel, and two agents attempted to write to the same destination path concurrently. The last write won but wrote incomplete content.

**Fix applied:** Corrupted agent files were restored from the ECC/Superpowers source patterns. Empty artifact files were deleted.

**Prevention:** Bootstrap steps that write to overlapping paths must run sequentially, not in parallel. The `project-bootstrap` skill now documents this constraint. Do not run `project-generate-agents` in parallel mode if output paths overlap.
