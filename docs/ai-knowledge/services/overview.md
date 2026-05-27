# Service Overview

This document covers all services in the OpenTelemetry Demo. Each row links to a per-service detail file.

Port values come from `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/.env`. The Kafka `orders` topic is the only Kafka topic in use.

## Core Business Services

| Service | Language | Framework | Port | Communication | OTel Approach |
|---|---|---|---|---|---|
| [accounting](./accounting.md) | C# / .NET 10 | ASP.NET Core | none exposed | Kafka consumer | .NET auto-instrumentation (instrument.sh) + manual ActivitySource |
| [ad](./ad.md) | Java 21 | gRPC Java | 9555 | gRPC | Java agent (JAVA_TOOL_OPTIONS) |
| [cart](./cart.md) | C# / .NET 10 | ASP.NET Core gRPC | 7070 | gRPC | .NET SDK manual + StackExchangeRedis instrumentation |
| [checkout](./checkout.md) | Go | gRPC Go + Sarama | 5050 | gRPC + Kafka producer + HTTP | Go SDK manual (otelgrpc, otelhttp, otelslog) |
| [currency](./currency.md) | C++ | gRPC C++ | 7001 | gRPC | C++ SDK manual |
| [email](./email.md) | Ruby | Sinatra | 6060 | HTTP | Ruby SDK + Sinatra auto-instrumentation |
| [fraud-detection](./fraud-detection.md) | Kotlin / JVM | Kafka consumer | none exposed | Kafka consumer | Java agent (JAVA_TOOL_OPTIONS) |
| [frontend](./frontend.md) | TypeScript | Next.js (Node SSR + React) | 8080 | gRPC (server) + HTTP (browser) | Node.js auto-instrumentations-node + browser OTLP |
| [frontend-proxy](./frontend-proxy.md) | N/A | Envoy | 8080, 10000 (admin) | HTTP + gRPC reverse proxy | Envoy native OTel tracing |
| [image-provider](./image-provider.md) | N/A | nginx | 8081 | HTTP static files | nginx ngx_otel_module |
| [load-generator](./load-generator.md) | Python | Locust + Playwright | 8089 | HTTP | Python SDK manual |
| [payment](./payment.md) | JavaScript | Node.js gRPC | 50051 | gRPC | Node.js auto-instrumentations-node |
| [product-catalog](./product-catalog.md) | Go | gRPC Go + PostgreSQL | 3550 | gRPC | Go SDK manual (otelgrpc, otelsql, otelslog) |
| [product-reviews](./product-reviews.md) | Python | gRPC Python + OpenAI | 3551 | gRPC + HTTP (LLM) | Python auto-instrumentation + manual spans |
| [quote](./quote.md) | PHP 8.4 | Slim Framework | 8090 | HTTP | PHP SDK (OTEL_PHP_AUTOLOAD_ENABLED) + manual tracer |
| [recommendation](./recommendation.md) | Python | gRPC Python | 9001 | gRPC | Python auto-instrumentation (opentelemetry-bootstrap) |
| [shipping](./shipping.md) | Rust | Actix-web | 50050 | HTTP | actix-web OTel middleware (RequestTracing, RequestMetrics) |

## Supporting / Infrastructure Services

| Service | Language | Framework | Port | Communication | OTel Approach |
|---|---|---|---|---|---|
| [flagd](./flagd.md) | N/A | flagd (open-feature) | 8013, 8016 (OFREP) | gRPC + HTTP | Built-in OTel metrics export |
| [flagd-ui](./flagd-ui.md) | Elixir | Phoenix LiveView | 4000 | HTTP | opentelemetry_exporter Elixir |
| [kafka](./kafka.md) | Java / JVM | Apache Kafka (KRaft) | 9092 | Kafka | Java agent via KAFKA_OPTS |
| [llm](./llm.md) | Python | Flask | 8000 | HTTP | None (mock LLM, no OTel) |
| [postgresql](./postgresql.md) | N/A | PostgreSQL 17 | 5432 | TCP/SQL | Scraped by otel-collector postgresql receiver |
| [valkey-cart](./valkey-cart.md) | N/A | Valkey 9 (Redis-compat) | 6379 | TCP | Scraped by otel-collector redis receiver |

## Telemetry Infrastructure

| Service | Framework | Port | Role |
|---|---|---|---|
| [otel-collector](./otel-collector.md) | OTel Collector Contrib | 4317 (gRPC), 4318 (HTTP) | Central OTLP receiver; routes to Jaeger, Prometheus, OpenSearch |
| [jaeger](./jaeger.md) | Jaeger 2.x | 16686 (UI), 4317 (gRPC) | Distributed trace storage and UI |
| [grafana](./grafana.md) | Grafana | 3000 | Metrics/logs dashboards |
| [prometheus](./prometheus.md) | Prometheus | 9090 | Metrics storage; OTLP receiver enabled |
| [opensearch](./opensearch.md) | OpenSearch 3.x | 9200 | Log storage |

## Kafka Topic Map

| Topic | Producer | Consumers |
|---|---|---|
| `orders` | checkout | accounting, fraud-detection |

## Key Protobuf Contracts

All gRPC services share a single protobuf contract at `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/pb/demo.proto`.

Services defined: CartService, RecommendationService, ProductCatalogService, ProductReviewService, ShippingService, CurrencyService, PaymentService, EmailService, CheckoutService, AdService.

Generated code locations:
- Go: `src/checkout/genproto/`, `src/product-catalog/genproto/`
- Python: `src/recommendation/demo_pb2*.py`, `src/product-reviews/demo_pb2*.py`
- TypeScript: `src/frontend/protos/demo.ts` (generated)
- C++: `src/currency/build/generated/proto/`

## Risky Change Areas

1. **`pb/demo.proto`** - any change breaks all language-specific generated stubs simultaneously across Go, Python, TypeScript, C++, C#, Java, Kotlin, Ruby, PHP, Rust. The generator script is `/Users/egormasnankin/work/ai-workshop/opentelemetry-demo/docker-gen-proto.sh`.
2. **Kafka `orders` topic schema** (protobuf `OrderResult`) - checkout produces, accounting and fraud-detection consume. A serialization change in checkout breaks both consumers with no compile-time warning.
3. **`OTEL_EXPORTER_OTLP_ENDPOINT` split** - some services use gRPC (default port 4317) and some hardcode HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`). Changing the collector address env var only updates services that inherit the default; hardcoded-HTTP services (accounting, ad, email, fraud-detection, quote, kafka, flagd-ui) must be updated separately.
4. **product-reviews LLM call chain** - product-reviews calls the llm service over HTTP using the OpenAI client; any change to LLM_BASE_URL, LLM_PORT, or LLM_MODEL breaks the AI assistant feature silently (no gRPC contract, plain HTTP).
5. **frontend gRPC to backend** - frontend calls ad, cart, checkout, currency, product-catalog, product-reviews, recommendation, and shipping directly via gRPC (not through frontend-proxy). If any of those services change their gRPC interface, the frontend TypeScript stubs from `src/frontend/protos/demo.ts` must be regenerated.
