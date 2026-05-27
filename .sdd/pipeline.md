# SDD Pipeline

This repository uses a two-stage AI coding harness:

1. Project intelligence harness (Setup 1 — complete)
2. SDD delivery pipeline (this file — Setup 2)

Setup 1 produced: project documentation, feature documentation, domain expert agents,
implementer agents, reviewer agents, and validation categories.

Setup 2 uses those assets to deliver features and bug fixes through SDD.

---

## Feature storage model

Stable feature docs:

```text
docs/features/{feature-area}/overview.md
docs/features/{feature-area}/detail.md
```

Active SDD work (one delivery iteration):

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Full example:

```text
docs/features/checkout-flow/
  overview.md
  detail.md
  changes/
    gift-wrap-checkout/
      01-design.md
      02-design-review.md
      03-implementation-plan.md
      04-plan-review.md
      tasks/
        task-01-backend.md
        task-01-backend.evidence.md
      verification/
        manual-test-cases.md
        final-verification-report.md
      final-report.md
```

Do not write SDD artifacts anywhere else.

---

## SDD lifecycle

### 1. `/sdd-start`

- Classify request (feature / bug / refactor / docs / investigation).
- Choose feature area from known areas or create one.
- Choose change slug (kebab-case, descriptive).
- Identify impacted services, contracts, telemetry, security, docs.
- Ask only blocking questions; convert ambiguity into explicit assumptions.
- Create `01-design.md`.
- Self-review the design.
- Ask user for approval.
- Output: `/sdd-review-design {feature-area}/{change-slug}`

### 2. `/sdd-review-design`

- Spawn selected design reviewers.
- Consolidate findings into `02-design-review.md`.
- Accept, reject (with rationale), debate once, or escalate to user.
- Apply accepted findings to `01-design.md`.
- Mark design APPROVED or NEEDS_REVISION.
- Output: `/sdd-plan {feature-area}/{change-slug}`

### 3. `/sdd-plan`

- Create code-near implementation plan in `03-implementation-plan.md`.
- Create one task file per independent unit of work in `tasks/*.md`.
- Create `verification/manual-test-cases.md`.
- Each task must name: owner_agent, reviewer_agents, services_touched, contracts_touched,
  frontend_impact, telemetry_impact, sensitive_data_impact, files_likely_touched,
  tests_to_write_first, commands_to_run, docs_to_update, evidence_file_path.
- Output: `/sdd-review-plan {feature-area}/{change-slug}`

### 4. `/sdd-review-plan`

- Spawn plan reviewers.
- Consolidate findings into `04-plan-review.md`.
- Accept, reject (with rationale), debate once, or escalate to user.
- Mark plan APPROVED or NEEDS_REVISION.
- Output: `/sdd-execute {feature-area}/{change-slug}`

### 5. `/sdd-execute`

Execute approved plan task by task using Superpowers-style subagent-driven development.

Per-task loop:

1. Extract full task text.
2. Select implementer from task `owner_agent`.
3. Dispatch implementer (fresh subagent, Sonnet model) with full context.
4. Implementer uses TDD for behavior changes.
5. Implementer runs relevant verification.
6. Implementer performs self-review and fixes findings.
7. Implementer reports: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED.
8. Orchestrator runs review sequence:
   - spec-compliance-reviewer (always)
   - domain-{service}-expert (if service logic changed)
   - technical-{language}-reviewer (always, per changed language)
   - observability-reviewer (always — mandatory per project rules)
   - security-data-leak-reviewer (always — mandatory per project rules)
   - test-verification-reviewer (always)
   - service-contract-reviewer (if proto/API changed)
   - distributed-flow-reviewer (if cross-service flow changed)
   - frontend-ui-kit-reviewer (if src/frontend/ changed)
   - code-quality-reviewer (only after spec compliance passes)
   - docs-consistency-reviewer (final gate)
9. Arbitrate findings: accept, reject with rationale, debate once,
   or escalate to user.
10. Send accepted findings back to implementer.
11. Re-review after fixes.
12. Write task evidence file.
13. Continue to next task without asking "should I continue?"

### 6. `/sdd-verify`

- Run automatic verification (trace tests, unit tests, lint).
- Run manual / browser verification per `verification/manual-test-cases.md`.
- Run final observability verification (spans, attributes, metrics).
- Run final spec compliance review.
- Write `verification/final-verification-report.md`.
- Do not claim completion without fresh evidence.

### 7. `/sdd-finalize`

- Update `docs/features/{feature-area}/overview.md`.
- Update `docs/features/{feature-area}/detail.md`.
- Update `docs/ai-knowledge/` if service behavior, communication,
  or observability changed.
- Run knowledge-curator.
- Run docs-consistency-reviewer.
- Write `final-report.md`.
- Create evidence markers in `.sdd/evidence/`.
- Keep change folder as delivery history.

---

## Human escalation rules

Stop and ask the user when:

- product behavior is unclear or scope changes,
- service boundary changes,
- public contract changes (proto),
- telemetry semantics change,
- sensitive data handling changes,
- rollout strategy changes,
- a reviewer finding affects architecture, security, or product,
- plan is wrong,
- verification repeatedly fails with no new information.

Never ask "should I continue?" when an approved plan has remaining tasks.

---

## Evidence rule

No completion claim without fresh verification evidence in `.sdd/evidence/`
or in the change's `verification/final-verification-report.md`.

---

## Hook policy

Hooks are used only for:

- dangerous command blocking,
- changed-file recording,
- optional final evidence guard.

Hooks are NOT the primary review mechanism. Semantic review is orchestrated by the
sdd-orchestrator agent through subagent dispatch.

---

## Known feature areas

| Feature Area | Stable Docs |
| --- | --- |
| checkout-flow | docs/features/checkout-flow/ |
| order-confirmation-email | docs/features/order-confirmation-email/ |
| product-browsing | docs/features/product-browsing/ |
| product-reviews | docs/features/product-reviews/ |
| recommendations | docs/features/recommendations/ |
| feature-flags | docs/features/feature-flags/ |

---

## Service → Implementer mapping

| Service(s) | Language | Implementer Agent |
| --- | --- | --- |
| frontend | TypeScript/React/Next.js | typescript-frontend-implementer |
| checkout, product-catalog | Go | go-implementer |
| accounting, cart | C#/.NET | csharp-dotnet-implementer |
| currency | C++ | cpp-implementer |
| flagd-ui | Elixir | elixir-implementer |
| ad, kafka | Java | java-implementer |
| payment | JavaScript/Node.js | javascript-node-implementer |
| fraud-detection | Kotlin | kotlin-implementer |
| quote | PHP | php-implementer |
| llm, load-generator, product-reviews, recommendation | Python | python-implementer |
| email | Ruby | ruby-implementer |
| shipping | Rust | rust-implementer |
| otel-collector, flagd, frontend-proxy, docker-compose, kubernetes/ | Infra/Config | infra-otel-implementer |

---

## Service → Domain expert mapping

`domain-{service-name}-expert` for each service under `src/{service-name}/`.

Example: `src/checkout/` → `domain-checkout-expert`

---

## Service → Technical reviewer mapping

| Language/Runtime | Technical Reviewer |
| --- | --- |
| TypeScript/React/Next.js | technical-typescript-reviewer |
| Go | technical-go-reviewer |
| Python | technical-python-reviewer |
| C#/.NET | technical-csharp-dotnet-reviewer |
| Java | technical-java-reviewer |
| Kotlin | technical-kotlin-reviewer |
| Rust | technical-rust-reviewer |
| PHP | technical-php-reviewer |
| Ruby | technical-ruby-reviewer |
| Elixir | technical-elixir-reviewer |
| JavaScript/Node.js | technical-javascript-node-reviewer |
| C++ | technical-cpp-reviewer |

---

## Validation priority order

1. Security / Data Leakage — PII in telemetry is an immediate blocker
2. Service Contract Compatibility — breaking proto changes block all services
3. Observability — incorrect telemetry defeats the purpose of this demo
4. Technical Correctness — correctness over style
5. Distributed Flow — trace propagation across services
6. Service Architecture and Project Rules
7. Domain Behavior
8. Testing / Verification Evidence
9. Code Quality — lowest priority
10. Frontend / UI-Kit — frontend changes only
11. Documentation Consistency
12. Knowledge Update Quality — after code review is complete

---

## Docs sources

| Category | Path |
| --- | --- |
| Architecture | docs/ai-knowledge/architecture/ |
| Services | docs/ai-knowledge/services/ |
| Communication | docs/ai-knowledge/communication/ |
| Frontend | docs/ai-knowledge/frontend/ |
| UI Kit | docs/ai-knowledge/ui-kit/ |
| Testing | docs/ai-knowledge/testing/ |
| Observability | docs/ai-knowledge/observability/ |
| Validation | docs/ai-knowledge/validation/ |
| Agents | docs/ai-knowledge/agents/ |
| Learning | docs/ai-knowledge/learning/ |
| Features | docs/features/ |

---

## Self-learning update rules

After finalization:

1. Run knowledge-curator to update docs/ai-knowledge/ where behavior changed.
2. Update docs/ai-knowledge/learning/iteration-log.md.
3. Propose updates via docs/ai-knowledge/learning/proposed-updates.md.
4. Rejected updates go to docs/ai-knowledge/learning/rejected-updates.md with rationale.
5. All updates reviewed by docs-consistency-reviewer before merge.

---

Last updated: 2026-05-27
