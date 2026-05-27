# Communication Overview

This document summarizes all inter-service communication in the OpenTelemetry Demo. Detailed tables are in the sibling files: `grpc-map.md`, `http-map.md`, `kafka-map.md`, `proto-contracts.md`.

---

## Services and Their Roles

| Service | Language | Role | Inbound Protocol | Outbound Calls |
|---------|----------|------|-----------------|----------------|
| frontend-proxy (Envoy) | — | Ingress router | HTTP | HTTP to frontend, image-provider, flagd, grafana, jaeger, loadgen |
| frontend | TypeScript (Next.js) | BFF + storefront | HTTP (browser + Envoy) | gRPC to ad/cart/checkout/currency/product-catalog/product-reviews/recommendation; HTTP to shipping |
| ad | Java | Ad selection | gRPC | flagd (OpenFeature SDK) |
| cart | C# (.NET) | Cart CRUD | gRPC | Valkey (Redis-compat) |
| checkout | Go | Order orchestration | gRPC | gRPC to cart/currency/payment/product-catalog; HTTP to shipping/email; Kafka producer |
| currency | C++ | Currency conversion | gRPC | none |
| email | Ruby (Sinatra) | Confirmation emails | HTTP | none (external SMTP stub via Pony) |
| payment | Node.js | Card charge | gRPC | none |
| product-catalog | Go | Product data | gRPC | PostgreSQL |
| product-reviews | Python | Product reviews + AI assistant | gRPC | gRPC to product-catalog; HTTP to llm |
| recommendation | Python | Recommendations | gRPC | gRPC to product-catalog |
| shipping | Rust (actix-web) | Shipping quotes + order dispatch | HTTP | HTTP to quote |
| quote | PHP (Slim) | Shipping cost calculation | HTTP | none |
| llm | Python (Flask) | Mock OpenAI API | HTTP | none |
| accounting | C# (.NET) | Order accounting | Kafka consumer | PostgreSQL |
| fraud-detection | Kotlin | Fraud logging | Kafka consumer | none |
| load-generator | Python (Locust) | Traffic generation | — | HTTP to frontend-proxy |
| flagd | external binary | Feature flags | gRPC (OpenFeature) / HTTP (OFREP) | none |
| kafka | JVM | Message broker | Kafka protocol | none |
| postgresql | PostgreSQL | Persistence | SQL | none |
| valkey-cart | Valkey | Cart storage | Redis protocol | none |

---

## Dependency Graph

```
Browser / load-generator
        |
        v
frontend-proxy (Envoy)
        |
        v
  frontend (Next.js BFF)
  |  |  |  |  |  |  |  \
  |  |  |  |  |  |  |   HTTP
  |  |  |  |  |  |  |    |
  |  |  |  |  |  |  |   shipping ----HTTP----> quote
  |  |  |  |  |  |  |
  gRPC (7 clients)
  |  |  |  |  |  |  |
  ad cart checkout currency product-catalog product-reviews recommendation
           |           |         |    ^           |     ^
           |           |         |    |           |     |
           |         gRPC      PostgreSQL       gRPC  gRPC
           |           |                         |
           |         payment                   product-catalog
           |
          gRPC to cart, currency, product-catalog, payment
          HTTP to shipping, email
          Kafka produce
             |
         "orders" topic
             |
          +--+--+
          |     |
       accounting  fraud-detection
       (C#)         (Kotlin)
          |
       PostgreSQL


product-reviews --> gRPC --> product-catalog
product-reviews --> HTTP --> llm (mock OpenAI)

All services --> OTel Collector --> Jaeger, Prometheus, OpenSearch
```

---

## Protocol Summary

### gRPC

- 10 proto services defined in `pb/demo.proto`
- frontend is the largest gRPC client (7 downstream stubs)
- checkout is the second largest gRPC client (4 downstream stubs)
- Generated code exists in Go, C++, Python, TypeScript, and is loaded at runtime in Node.js
- See `grpc-map.md` for full caller/callee table

### HTTP

- shipping and email are proto-defined services but implemented as HTTP servers (Rust actix-web, Ruby Sinatra)
- checkout calls both over plain HTTP POST, not gRPC
- frontend has an HTTP gateway only for shipping (`src/frontend/gateways/http/Shipping.gateway.ts`)
- shipping calls quote over HTTP
- product-reviews calls llm over HTTP (OpenAI-compatible API)
- See `http-map.md` for full endpoint and client table

### Kafka

- One topic: `orders`
- One producer: checkout (Go, sarama async)
- Two consumers: accounting (C#, Confluent.Kafka) and fraud-detection (Kotlin, standard consumer)
- Message format: protobuf `OrderResult`
- See `kafka-map.md` for full flow

---

## Top Risky Flows

These are the flows most likely to cause silent failures or cascading bugs if changed:

1. **Proto file changes affect 7 languages simultaneously** — `pb/demo.proto` has no regeneration automation at the repo root. Changes require coordinated updates to Go, C++, Python, TypeScript, and Node.js runtime loading. Evidence: `grpc-map.md` generated code table, `proto-contracts.md` risk table.

2. **checkout silently skips Kafka when `KAFKA_ADDR` is unset** — `src/checkout/main.go:386-389`. Orders complete without triggering accounting or fraud-detection. This is intentional for minimal deployments but invisible at the API level.

3. **Kafka producer uses no-ack mode** — `src/checkout/kafka/producer.go:41`. Messages can be lost without the order failing. The `kafkaQueueProblems` feature flag amplifies this by flooding the topic.

4. **`OrderResult` is the Kafka message schema** — shared between checkout (producer), accounting, and fraud-detection. Any field change in `pb/demo.proto` requires all three services to redeploy atomically. There is no schema registry or compatibility enforcement.

5. **Double HTTP hop for shipping cost** — browser → frontend → shipping → quote. The quote service is only reachable through shipping; there is no direct path. A slow quote service blocks frontend shipping cost display.

6. **camelCase/snake_case translation at two independent points** — both `src/frontend/gateways/http/Shipping.gateway.ts` and `src/checkout/main.go` manually transform address/cart item field names before sending to shipping. If shipping's JSON schema changes, both callers need independent updates.

7. **product-reviews LLM URL selection by feature flag** — `src/product-reviews/product_reviews_server.py:166-200`. The `llmRateLimitError` flag controls whether mock or real LLM URL is used, and can silently redirect production traffic to the mock server.

8. **recommendation cache leak under feature flag** — `src/recommendation/recommendation_server.py:79-87`. When `recommendationCacheFailure` is enabled, `cached_ids` grows unboundedly in memory, eventually exhausting the container's 500M limit.
