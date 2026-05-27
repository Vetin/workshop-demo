# SDD Agent Routing

Use this document to decide which agents to dispatch during `/sdd-execute`.

## Always required after each implementation task

- `spec-compliance-reviewer`
- `observability-reviewer`
- `security-data-leak-reviewer`
- `test-verification-reviewer`
- `code-quality-reviewer` (only after spec-compliance-reviewer passes)
- `docs-consistency-reviewer`

## Domain expert routing

Run `domain-{service}-expert` when files under a service path changed.

| Path changed | Domain expert |
| --- | --- |
| src/frontend/ | domain-frontend-expert |
| src/checkout/ | domain-checkout-expert |
| src/cart/ | domain-cart-expert |
| src/payment/ | domain-payment-expert |
| src/email/ | domain-email-expert |
| src/product-catalog/ | domain-product-catalog-expert |
| src/shipping/ | domain-shipping-expert |
| src/quote/ | domain-quote-expert |
| src/currency/ | domain-currency-expert |
| src/recommendation/ | domain-recommendation-expert |
| src/product-reviews/ | domain-product-reviews-expert |
| src/llm/ | domain-llm-expert |
| src/accounting/ | domain-accounting-expert |
| src/fraud-detection/ | domain-fraud-detection-expert |
| src/ad/ | domain-ad-expert |
| src/kafka/ | domain-kafka-expert |
| src/flagd-ui/ | domain-flagd-ui-expert |
| src/flagd/ | domain-flagd-expert |
| src/otel-collector/ | domain-otel-collector-expert |
| src/grafana/ | domain-grafana-expert |
| src/image-provider/ | domain-image-provider-expert |
| src/jaeger/ | domain-jaeger-expert |
| src/opensearch/ | domain-opensearch-expert |
| src/postgresql/ | domain-postgresql-expert |
| src/prometheus/ | domain-prometheus-expert |
| src/valkey-cart/ | domain-valkey-cart-expert |
| src/frontend-proxy/ | domain-frontend-proxy-expert |
| src/load-generator/ | domain-load-generator-expert |

Use `docs/ai-knowledge/services/service-inventory.json` as the authoritative
source for service paths.

## Technical reviewer routing

Run the technical reviewer for each changed language/runtime:

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

## Conditional cross-cutting reviewers

Run `service-contract-reviewer` when:

- `pb/demo.proto` changed,
- any generated stub file changed (`.pb.go`, `_pb2.py`, `demo_pb.js`, etc.),
- a new gRPC method is added or an existing one is modified,
- an HTTP route is added or modified in email or shipping services.

Run `distributed-flow-reviewer` when:

- a new cross-service call is introduced,
- data transformation crosses service boundaries,
- trace context propagation paths change.

Run `frontend-ui-kit-reviewer` when:

- any file under `src/frontend/` changed,
- styled-components theme tokens changed,
- UI accessibility (ARIA) changes made,
- OTel browser instrumentation changed,
- frontend API layer changed.

Run `security-data-leak-reviewer` when (additionally triggered explicitly):

- payment, email, user text, gift messages changed,
- logs, telemetry, or event payloads changed,
- any new data flows through spans or Kafka messages.

Run `knowledge-curator` when:

- `docs/ai-knowledge/` changed,
- `docs/features/` changed,
- a self-learning update was proposed.

## Verification-stage routing

During /sdd-verify:

Always run:
- browser-manual-verifier when the change affects user-visible UI or browser-observable behavior.
- e2e-test-author after manual browser verification passes.
- e2e-test-reviewer after E2E tests are added or planned.
- test-verification-reviewer before final verification report.
- docs-consistency-reviewer before finalization.

Run frontend-ui-kit-reviewer when:
- UI components changed,
- local UI-kit changed,
- Figma mapping changed,
- styling or design behavior changed.

Run distributed-flow-reviewer when:
- browser behavior depends on multiple services,
- checkout/payment/shipping/email flow changed,
- frontend API behavior changed.

Run observability-reviewer when:
- traces, metrics, logs, or telemetry attributes changed.

Run security-data-leak-reviewer when:
- user-entered text appears in UI, email, logs, events, or telemetry.
