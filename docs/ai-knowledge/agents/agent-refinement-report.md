# Agent Refinement Report

**Date:** 2026-05-27
**Skill:** `project-refine-agents`
**Reviewer:** project-refine-agents skill + docs-consistency-reviewer + knowledge-curator

---

## Summary

All `.claude/agents/` files were audited and refined against the actual
OpenTelemetry Demo codebase. The harness now contains domain-specific agents
with correct service paths, structured output formats, and complete routing
documentation.

---

## Inventory

| Category | Count (after refinement) |
|---|---|
| Orchestrator | 1 |
| Domain experts | 28 |
| Implementers | 13 |
| Technical reviewers | 12 |
| Specialized reviewers | 6 |
| Knowledge maintainers | 3 |
| Bootstrap mappers | 7 |
| Pattern reviewers | 2 |
| **Total active** | **72** |
| Legacy (archived) | 2 |
| Artifacts deleted | 3 |

---

## Changes Made

### Critical Bug Fixes

| File | Issue | Fix Applied |
|---|---|---|
| `sdd-orchestrator.md` | Severely corrupted — garbled repeated text, broken step 4 | Reconstructed from scratch |
| `service-boundary-mapper.md` | Severely corrupted — garbled output paths, broken YAML | Reconstructed with full service path inventory |
| `technical-go-reviewer.md` | Wrong scope paths (`src/checkoutservice/`, `src/productcatalogservice/`) | Fixed to `src/checkout/`, `src/product-catalog/` |
| `technical-python-reviewer.md` | Wrong scope paths (`src/loadgenerator/`, `src/productreviewsservice/`, etc.) | Fixed all 4 paths |
| `observability-reviewer.md` | Wrong scope paths (`src/otelcollector/`, `src/loadgenerator/`) | Fixed both paths |

### Legacy Agents Archived

| Agent | Reason | Replacement |
|---|---|---|
| `technical-csharp-reviewer` | Duplicate with wrong paths (`src/accountingservice/`, `src/cartservice/`) | `technical-csharp-dotnet-reviewer` |
| `technical-javascript-reviewer` | Duplicate with wrong path (`src/paymentservice/`) | `technical-javascript-node-reviewer` |

Archived to: `docs/ai-knowledge/agents/legacy/`

### Empty Artifact Files Deleted

- `.claude/agents/com:` (0 bytes)
- `.claude/agents/communication-flow-macat` (0 bytes)
- `.claude/agents/cper` (0 bytes)

### New Documentation Created

#### Language Knowledge (`docs/ai-knowledge/languages/`)

| File | Coverage |
|---|---|
| `overview.md` | Master table: all services → language/runtime + proto/test sections |
| `go.md` | checkout, product-catalog: Go 1.24+, otelgrpc, otelsql (XSAM), build/test commands |
| `python.md` | llm, load-generator, product-reviews, recommendation: per-service OTel strategy |
| `dotnet.md` | accounting, cart: instrument.sh entrypoint rule, ActivitySource pattern |
| `java-kotlin.md` | ad (Java), fraud-detection (Kotlin), kafka config |
| `nodejs.md` | payment: proto loading discipline, span.end() in finally |
| `typescript-nextjs.md` | frontend: Pages Router only, dual SSR+browser OTel |
| `rust.md` | shipping: `opentelemetry_instrumentation_actix_web`, no .unwrap() rule |
| `ruby.md` | email: Sinatra, OTel SDK init order |
| `php.md` | quote: OTEL_PHP_AUTOLOAD_ENABLED, manual tracer with finally |
| `cpp.md` | currency: CMake, OpenTelemetry C++ SDK |
| `infra-config.md` | flagd JSON, Envoy, nginx, OTel Collector, Prometheus, Grafana |

#### Agent Knowledge (`docs/ai-knowledge/agents/`)

- `agent-catalog.md` — Full inventory table (72 active agents + 2 legacy)
- `agent-routing.md` — Language→implementer, service→domain-expert, reviewer dispatch rules
- `agent-design-decisions.md` — Superpowers/ECC pattern reuse decisions

#### Validation Knowledge (`docs/ai-knowledge/validation/`)

- `reviewer-routing.md` — 13-change-type reviewer dispatch table
- `stop-hook-policy.md` — SubagentStop gate sequence, implementer obligations
- `validation-categories.md` — 13 validation categories with responsible agents

### Agent Enhancements

#### All 28 Domain Expert Agents

Each `domain-*-expert.md` agent received 7 new sections appended after
`## Rules`:

1. **When to use this agent** — specific to the service
2. **Inbound communication** — which services call this one
3. **Outbound communication** — which services this one calls
4. **Relevant test commands** — build and trace-test commands
5. **What to review** — scope of this agent's expertise
6. **What NOT to review** — explicit scope boundaries
7. **Required output format** — YAML verdict/findings/docs_to_update/unknowns

#### All 13 Implementer Agents

Each `*-implementer.md` agent received a new section at the end:

**`## Stop Behavior and Evidence Requirements`** — documents that implementers
must not claim completion themselves, that SubagentStop hooks run gates
automatically, and what implementers must cite before stopping.

#### Bootstrap Agent Rebuilds

- `observability-mapper.md` — rebuilt with 8-item capture checklist, per-language
  grep patterns, output file rules
- `feature-documenter.md` — rebuilt with when-to-use, input sources, output targets,
  required 7-section output format

---

## Self-Review Findings and Resolutions

### docs-consistency-reviewer

| Finding | Severity | Resolution |
|---|---|---|
| `agent-catalog.md` and `agent-routing.md` used upstream-style paths (`src/accountingservice/`, etc.) — 16 services affected | Major | Bulk sed replacement applied across both files + `reviewer-routing.md` |
| `reviewer-routing.md` line 16: `src/otelcollector/` | Minor | Fixed to `src/otel-collector/` |
| `agent-catalog.md` domain-llm-expert row conflated with recommendation path | Minor | Fixed to `src/llm/` |
| `agent-catalog.md` domain-postgresql-expert row said `src/accounting/ DB` | Minor | Fixed to `src/postgresql/` |
| `agent-catalog.md` domain-valkey-cart-expert row said `src/cart/ cache layer` | Minor | Fixed to `src/valkey-cart/` |
| `AGENTS.md` missing (referenced from `CLAUDE.md` via `@AGENTS.md`) | Pre-existing gap | Not in scope of this skill; noted for future work |

### knowledge-curator

| Finding | Severity | Resolution |
|---|---|---|
| `go.md`: Go version stated as `1.22+`; actual is `1.24.2` | Major | Fixed in `go.md` and `overview.md` |
| `go.md`: OTel SQL package wrong (`go.opentelemetry.io/...otelsql`); actual is `github.com/XSAM/otelsql` | Major | Fixed with third-party note |
| `go.md`: Span naming example `"checkout.PlaceOrder"` doesn't match actual code | Minor | Removed forced convention, replaced with descriptive-name guidance |
| `rust.md`: Wrong crate `actix_web_opentelemetry`; actual is `opentelemetry_instrumentation_actix_web` | Major | Fixed in `rust.md` |
| `python.md`: Referenced `CMD` for ENTRYPOINT-based OTel bootstrap | Minor | Fixed to `ENTRYPOINT` |
| `agent-catalog.md`: Legacy path said `.claude/agents/legacy/`; actual is `docs/ai-knowledge/agents/legacy/` | Minor | Fixed |
| `agent-routing.md`: shipping protocol listed as gRPC; actual is HTTP (Actix-web) | Major | Fixed |
| `agent-routing.md`: checkout port listed as 8080; actual gRPC port is 5050 | Minor | Fixed |
| `src/react-native-app/` not covered by any agent or language file | Gap | Added out-of-scope note to `overview.md` |

---

## Completion Checklist

- [x] Every active agent has a precise role
- [x] Every active agent has a clear description
- [x] Every reviewer is read-only (no Edit/Write tools)
- [x] Every implementer is scoped to its language/service set
- [x] Every domain expert maps to a real service/module
- [x] Every implementer maps to a real language/runtime
- [x] Every technical reviewer maps to a real language/runtime
- [x] Every active agent references relevant `docs/ai-knowledge`
- [x] Every legacy agent is archived with reason
- [x] Agent routing docs updated
- [x] Validation routing docs updated
- [x] Self-review passed (all major/minor findings resolved)
- [x] `src/react-native-app/` explicitly noted as out-of-scope
- [ ] `AGENTS.md` missing (pre-existing gap — not in scope of this skill)
