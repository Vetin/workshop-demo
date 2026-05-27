# Agent Catalog

Complete inventory of all Claude Code agents in `.claude/agents/` for the OpenTelemetry Demo SDD harness.

Last updated: 2026-05-27

---

## Inventory Table

| Name | Category | Can Edit Files? | Model | Assigned Service(s) / Scope | Status |
|------|----------|-----------------|-------|------------------------------|--------|
| sdd-orchestrator | orchestrator | no (read-only tools only) | sonnet | entire repo — routes all SDD work | active |
| domain-accounting-expert | domain-expert | no | sonnet | accounting (src/accounting/) | active |
| domain-ad-expert | domain-expert | no | sonnet | ad (src/ad/) | active |
| domain-cart-expert | domain-expert | no | sonnet | cart (src/cart/) | active |
| domain-checkout-expert | domain-expert | no | sonnet | checkout (src/checkout/) | active |
| domain-currency-expert | domain-expert | no | sonnet | currency (src/currency/) | active |
| domain-email-expert | domain-expert | no | sonnet | email (src/email/) | active |
| domain-flagd-expert | domain-expert | no | sonnet | flagd (src/flagd/) | active |
| domain-flagd-ui-expert | domain-expert | no | sonnet | flagd-ui (src/flagd-ui/) | active |
| domain-fraud-detection-expert | domain-expert | no | sonnet | fraud-detection (src/fraud-detection/) | active |
| domain-frontend-expert | domain-expert | no | sonnet | frontend (src/frontend/) | active |
| domain-frontend-proxy-expert | domain-expert | no | sonnet | frontend-proxy (src/frontend-proxy/) | active |
| domain-grafana-expert | domain-expert | no | sonnet | grafana (src/grafana/) | active |
| domain-image-provider-expert | domain-expert | no | sonnet | image-provider (src/image-provider/) | active |
| domain-jaeger-expert | domain-expert | no | sonnet | jaeger (src/jaeger/) | active |
| domain-kafka-expert | domain-expert | no | sonnet | kafka (src/kafka/) | active |
| domain-llm-expert | domain-expert | no | sonnet | llm (src/llm/) | active |
| domain-load-generator-expert | domain-expert | no | sonnet | load-generator (src/load-generator/) | active |
| domain-opensearch-expert | domain-expert | no | sonnet | opensearch (src/opensearch/) | active |
| domain-otel-collector-expert | domain-expert | no | sonnet | otel-collector (src/otel-collector/) | active |
| domain-payment-expert | domain-expert | no | sonnet | payment (src/payment/) | active |
| domain-postgresql-expert | domain-expert | no | sonnet | postgresql (src/postgresql/) | active |
| domain-product-catalog-expert | domain-expert | no | sonnet | product-catalog (src/product-catalog/) | active |
| domain-product-reviews-expert | domain-expert | no | sonnet | product-reviews (src/product-reviews/) | active |
| domain-prometheus-expert | domain-expert | no | sonnet | prometheus (src/prometheus/) | active |
| domain-quote-expert | domain-expert | no | sonnet | quote (src/quote/) | active |
| domain-recommendation-expert | domain-expert | no | sonnet | recommendation (src/recommendation/) | active |
| domain-shipping-expert | domain-expert | no | sonnet | shipping (src/shipping/) | active |
| domain-valkey-cart-expert | domain-expert | no | sonnet | valkey-cart (src/valkey-cart/ — no app code, Valkey 9 config) | active |
| cpp-implementer | implementer | yes | sonnet | currency (src/currency/) — C++ | active |
| csharp-dotnet-implementer | implementer | yes | sonnet | accounting (src/accounting/), cart (src/cart/) — C#/.NET | active |
| elixir-implementer | implementer | yes | sonnet | flagd-ui (src/flagd-ui/) — Elixir | active |
| go-implementer | implementer | yes | sonnet | checkout (src/checkout/), product-catalog (src/product-catalog/) — Go | active |
| infra-otel-implementer | implementer | yes | sonnet | otel-collector (src/otel-collector/), flagd (src/flagd/), frontend-proxy (src/frontend-proxy/), docker-compose.yml, k8s/ — infra/config | active |
| java-implementer | implementer | yes | sonnet | ad (src/ad/), kafka (src/kafka/) — Java | active |
| javascript-node-implementer | implementer | yes | sonnet | payment (src/payment/) — JavaScript/Node.js | active |
| kotlin-implementer | implementer | yes | sonnet | fraud-detection (src/fraud-detection/) — Kotlin | active |
| php-implementer | implementer | yes | sonnet | quote (src/quote/) — PHP | active |
| python-implementer | implementer | yes | sonnet | llm, load-generator (src/load-generator/), product-reviews (src/product-reviews/), recommendation (src/recommendation/) — Python | active |
| ruby-implementer | implementer | yes | sonnet | email (src/email/) — Ruby | active |
| rust-implementer | implementer | yes | sonnet | shipping (src/shipping/) — Rust | active |
| typescript-frontend-implementer | implementer | yes | sonnet | frontend (src/frontend/) — TypeScript/React | active |
| technical-cpp-reviewer | technical-reviewer | no | sonnet | currency (src/currency/) — C++ | active |
| technical-csharp-dotnet-reviewer | technical-reviewer | no | sonnet | accounting (src/accounting/), cart (src/cart/) — C#/.NET | active |
| technical-elixir-reviewer | technical-reviewer | no | sonnet | flagd-ui (src/flagd-ui/) — Elixir | active |
| technical-go-reviewer | technical-reviewer | no | sonnet | checkout (src/checkout/), product-catalog (src/product-catalog/) — Go | active |
| technical-java-reviewer | technical-reviewer | no | sonnet | ad (src/ad/), kafka (src/kafka/) — Java | active |
| technical-javascript-node-reviewer | technical-reviewer | no | sonnet | payment (src/payment/) — JavaScript/Node.js | active |
| technical-kotlin-reviewer | technical-reviewer | no | sonnet | fraud-detection (src/fraud-detection/) — Kotlin | active |
| technical-php-reviewer | technical-reviewer | no | sonnet | quote (src/quote/) — PHP | active |
| technical-python-reviewer | technical-reviewer | no | sonnet | llm, load-generator, product-reviews, recommendation — Python | active |
| technical-ruby-reviewer | technical-reviewer | no | sonnet | email (src/email/) — Ruby | active |
| technical-rust-reviewer | technical-reviewer | no | sonnet | shipping (src/shipping/) — Rust | active |
| technical-typescript-reviewer | technical-reviewer | no | sonnet | frontend (src/frontend/) — TypeScript/React | active |
| docs-consistency-reviewer | specialized-reviewer | no | sonnet | entire repo — doc accuracy vs code | active |
| frontend-ui-kit-reviewer | specialized-reviewer | no | sonnet | src/frontend/ — styled-components, theme, a11y, OTel browser | active |
| observability-reviewer | specialized-reviewer | no | sonnet | entire repo — OTel instrumentation, semantic conventions | active |
| security-data-leak-reviewer | specialized-reviewer | no | sonnet | entire repo — PII in spans/logs | active |
| service-contract-reviewer | specialized-reviewer | no | sonnet | pb/demo.proto, all generated stubs | active |
| test-verification-reviewer | specialized-reviewer | no | sonnet | test/tracetesting/, cypress/, span coverage | active |
| docs-simplifier | knowledge-maintainer | yes | sonnet | docs/ai-knowledge/ — simplifies/bootstraps docs | active |
| feature-documenter | knowledge-maintainer | yes | sonnet | docs/features/ — documents completed features | active |
| knowledge-curator | knowledge-maintainer | yes | sonnet | docs/ai-knowledge/ — maintains knowledge after implementation | active |
| communication-flow-mapper | bootstrap | no | sonnet | inter-service communication map — run once | active |
| frontend-architecture-mapper | bootstrap | no | sonnet | frontend component/page structure — run once | active |
| observability-mapper | bootstrap | no | sonnet | OTel instrumentation inventory — run once | active |
| proto-contract-mapper | bootstrap | yes | sonnet | pb/demo.proto contract map — run once | active |
| repo-cartographer | bootstrap | no | haiku | repository structure map — run once | active |
| service-boundary-mapper | bootstrap | no | sonnet | service boundary definitions — run once | active |
| ui-kit-cartographer | bootstrap | no | sonnet | UI kit/theme inventory — run once | active |
| ecc-agent-pattern-reviewer | pattern-reviewer | no | sonnet | ECC pattern extraction — bootstrap only | active |
| superpowers-method-reviewer | pattern-reviewer | no | sonnet | Superpowers pattern extraction — bootstrap only | active |
| test-command-discoverer | utility | no | haiku | discovers test commands per service — run on demand | active |
| technical-csharp-reviewer | legacy | no | sonnet | replaced by technical-csharp-dotnet-reviewer | legacy |
| technical-javascript-reviewer | legacy | no | sonnet | replaced by technical-javascript-node-reviewer | legacy |

---

## Empty Artifact Files Cleaned

The following empty non-markdown files were present in `.claude/agents/` from a corrupted `project-generate-agents` run on 2026-05-27 and have been removed:

- `com:` — empty file, artifact of truncated write
- `communication-flow-macat` — empty file, truncated version of `communication-flow-mapper.md`
- `cper` — empty file, artifact of truncated write

These were confirmed empty (no content) and are not valid agent definitions. The corresponding legitimate agent files (`communication-flow-mapper.md`, etc.) exist correctly as `.md` files.

---

## Category Counts

| Category | Count |
|----------|-------|
| orchestrator | 1 |
| domain-expert | 28 |
| implementer | 13 |
| technical-reviewer | 12 |
| specialized-reviewer | 6 |
| knowledge-maintainer | 3 |
| bootstrap | 7 |
| pattern-reviewer | 2 |
| utility | 1 |
| legacy | 2 |
| **Total** | **75** |

Note: 73 active agents are in `.claude/agents/*.md`. The 2 legacy agent records
are archived in `docs/ai-knowledge/agents/legacy/` and must not be dispatched.
