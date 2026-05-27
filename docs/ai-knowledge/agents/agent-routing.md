# Agent Routing Guide

How to dispatch the right agent for each situation in the SDD harness.

Last updated: 2026-05-27

---

## 1. Which implementer handles each language/runtime?

| Language / Runtime | Implementer Agent | Service Paths |
|--------------------|-------------------|---------------|
| C++ | cpp-implementer | src/currency/ |
| C# / .NET | csharp-dotnet-implementer | src/accounting/, src/cart/ |
| Elixir | elixir-implementer | src/flagd-ui/ |
| Go | go-implementer | src/checkout/, src/product-catalog/ |
| Infra / Config | infra-otel-implementer | src/otel-collector/, src/flagd/, src/frontend-proxy/, docker-compose.yml, k8s/ |
| Java | java-implementer | src/ad/, src/kafka/ |
| JavaScript / Node.js | javascript-node-implementer | src/payment/ |
| Kotlin | kotlin-implementer | src/fraud-detection/ |
| PHP | php-implementer | src/quote/ |
| Python | python-implementer | src/load-generator/, src/product-reviews/, src/recommendation/ |
| Ruby | ruby-implementer | src/email/ |
| Rust | rust-implementer | src/shipping/ |
| TypeScript / React | typescript-frontend-implementer | src/frontend/ |

---

## 2. Which domain expert handles each service?

| Service | Domain Expert | Language | Key Port | Communication Type |
|---------|--------------|----------|----------|-------------------|
| accounting | domain-accounting-expert | C# | 8080 | Kafka consumer |
| ad | domain-ad-expert | Java | 8080 | gRPC |
| cart | domain-cart-expert | C# | 8080 | gRPC; Valkey backend |
| checkout | domain-checkout-expert | Go | 5050 | gRPC; orchestrates many services |
| currency | domain-currency-expert | C++ | 8080 | gRPC |
| email | domain-email-expert | Ruby | 8080 | gRPC |
| flagd | domain-flagd-expert | — (config) | 8013 | feature-flag HTTP/gRPC |
| flagd-ui | domain-flagd-ui-expert | Elixir | 4000 | HTTP |
| fraud-detection | domain-fraud-detection-expert | Kotlin | 8080 | Kafka consumer |
| frontend | domain-frontend-expert | TypeScript/React | 8080 | HTTP/REST to BFF |
| frontend-proxy | domain-frontend-proxy-expert | Envoy (config) | 8080 | HTTP proxy |
| grafana | domain-grafana-expert | — (config) | 3000 | dashboard / scrape |
| image-provider | domain-image-provider-expert | — (nginx config) | 8081 | HTTP static |
| jaeger | domain-jaeger-expert | — (config) | 16686 | OTLP receiver / UI |
| kafka | domain-kafka-expert | Java | — | Kafka broker |
| llm | domain-llm-expert | Python | 8080 | HTTP (OpenAI-compat) |
| load-generator | domain-load-generator-expert | Python (Locust) | 8089 | HTTP load gen |
| opensearch | domain-opensearch-expert | — (config) | 9200 | search / OTLP exporter |
| otel-collector | domain-otel-collector-expert | — (config) | 4317/4318 | OTLP receiver/exporter |
| payment | domain-payment-expert | JavaScript/Node.js | 8080 | gRPC |
| postgresql | domain-postgresql-expert | — (config) | 5432 | SQL (accounting DB) |
| product-catalog | domain-product-catalog-expert | Go | 8080 | gRPC |
| product-reviews | domain-product-reviews-expert | Python | 8080 | HTTP/REST |
| prometheus | domain-prometheus-expert | — (config) | 9090 | metrics scrape |
| quote | domain-quote-expert | PHP | 8080 | gRPC |
| recommendation | domain-recommendation-expert | Python | 8080 | gRPC |
| shipping | domain-shipping-expert | Rust | 8080 | HTTP |
| valkey-cart | domain-valkey-cart-expert | — (Redis-compat) | 6379 | cache for cart service |

---

## 3. Which technical reviewer handles each language/runtime?

| Language / Runtime | Technical Reviewer | Services Covered |
|--------------------|-------------------|-----------------|
| C++ | technical-cpp-reviewer | currency |
| C# / .NET | technical-csharp-dotnet-reviewer | accounting, cart |
| Elixir | technical-elixir-reviewer | flagd-ui |
| Go | technical-go-reviewer | checkout, product-catalog |
| Java | technical-java-reviewer | ad, kafka |
| JavaScript / Node.js | technical-javascript-node-reviewer | payment |
| Kotlin | technical-kotlin-reviewer | fraud-detection |
| PHP | technical-php-reviewer | quote |
| Python | technical-python-reviewer | llm, load-generator, product-reviews, recommendation |
| Ruby | technical-ruby-reviewer | email |
| Rust | technical-rust-reviewer | shipping |
| TypeScript / React | technical-typescript-reviewer | frontend |

---

## 4. Which reviewers always run after any implementation?

These reviewers are mandatory after every implementation, regardless of which service changed:

1. **observability-reviewer** — verifies OTel span attributes, metric names, and semantic conventions are correct. Runs first because every service produces telemetry.
2. **docs-consistency-reviewer** — verifies that docs/ai-knowledge/ and docs/features/ accurately describe the changed code.
3. **security-data-leak-reviewer** — checks that no PII (email, card number, user ID, etc.) appears in span attributes or log bodies.

---

## 5. Which reviewers run conditionally?

| Condition | Reviewer(s) to Dispatch |
|-----------|------------------------|
| `pb/demo.proto` changes OR any generated proto stub changes | service-contract-reviewer |
| `src/frontend/` files change | frontend-ui-kit-reviewer |
| `test/tracetesting/` changes OR new OTel spans are added | test-verification-reviewer |
| Cross-service communication changes (new call, new endpoint, protocol change) | service-contract-reviewer |
| A specific service's files change | domain-{service}-expert for that service |
| Kafka schema changes | service-contract-reviewer + domain-checkout-expert + domain-accounting-expert + domain-fraud-detection-expert |

---

## 6. Which agents are forbidden from editing files?

The following agents have read-only tool sets (`Read, Grep, Glob, Bash` only) and must never write or modify files:

**All domain experts (28):**
domain-accounting-expert, domain-ad-expert, domain-cart-expert, domain-checkout-expert, domain-currency-expert, domain-email-expert, domain-flagd-expert, domain-flagd-ui-expert, domain-fraud-detection-expert, domain-frontend-expert, domain-frontend-proxy-expert, domain-grafana-expert, domain-image-provider-expert, domain-jaeger-expert, domain-kafka-expert, domain-llm-expert, domain-load-generator-expert, domain-opensearch-expert, domain-otel-collector-expert, domain-payment-expert, domain-postgresql-expert, domain-product-catalog-expert, domain-product-reviews-expert, domain-prometheus-expert, domain-quote-expert, domain-recommendation-expert, domain-shipping-expert, domain-valkey-cart-expert

**All specialized reviewers (6):**
docs-consistency-reviewer, frontend-ui-kit-reviewer, observability-reviewer, security-data-leak-reviewer, service-contract-reviewer, test-verification-reviewer

**All technical reviewers (12):**
technical-cpp-reviewer, technical-csharp-dotnet-reviewer, technical-elixir-reviewer, technical-go-reviewer, technical-java-reviewer, technical-javascript-node-reviewer, technical-kotlin-reviewer, technical-php-reviewer, technical-python-reviewer, technical-ruby-reviewer, technical-rust-reviewer, technical-typescript-reviewer

**Most bootstrap mappers (6 of 7):**
communication-flow-mapper, frontend-architecture-mapper, observability-mapper, repo-cartographer, service-boundary-mapper, ui-kit-cartographer

**Pattern reviewers (2):**
ecc-agent-pattern-reviewer, superpowers-method-reviewer

**Utility (1):**
test-command-discoverer

Note: `proto-contract-mapper` is the one bootstrap agent that has edit tools (used to write its output map file). The orchestrator (`sdd-orchestrator`) has no `tools:` field set, meaning it uses default Claude Code tools.

---

## 7. Which agents are used only during bootstrap/setup?

These agents run once (or rarely) to populate project knowledge and are not part of the regular SDD implementation loop:

| Agent | Purpose | When to Re-run |
|-------|---------|----------------|
| communication-flow-mapper | Maps inter-service call graph | When service topology changes significantly |
| frontend-architecture-mapper | Maps React component/page structure | When frontend architecture is restructured |
| observability-mapper | Inventories all OTel instrumentation across services | When new services are added |
| proto-contract-mapper | Documents all gRPC contracts from pb/demo.proto | When proto file is substantially updated |
| repo-cartographer | Generates top-level repo structure overview | When new top-level directories appear |
| service-boundary-mapper | Defines canonical service boundaries | When new services are added |
| ui-kit-cartographer | Inventories styled-components theme tokens and UI kit | When design system changes significantly |
| ecc-agent-pattern-reviewer | Extracted patterns from ECC — one-time setup | Not needed again |
| superpowers-method-reviewer | Extracted patterns from Superpowers — one-time setup | Not needed again |

---

## 8. Which agents are legacy and replaced?

| Legacy Agent | Replaced By | Reason |
|--------------|-------------|--------|
| technical-csharp-reviewer | technical-csharp-dotnet-reviewer | Renamed to reflect .NET runtime scope (covers both C# and .NET-specific patterns) |
| technical-javascript-reviewer | technical-javascript-node-reviewer | Renamed to reflect Node.js runtime scope (not browser JS) |

Both legacy agents are stored in `docs/ai-knowledge/agents/legacy/` and must not
be dispatched. The replacements are the active agents.
