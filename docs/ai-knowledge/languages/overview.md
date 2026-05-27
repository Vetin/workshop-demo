# Language/Runtime Overview

This file maps every service in the OpenTelemetry Demo (Astronomy Shop) to its
language, runtime, and primary frameworks. Use it as the entry point before
opening a language-specific knowledge file.

## Service-to-Language Map

| Service | Directory | Language / Runtime | Framework / Key Libs |
|---|---|---|---|
| accounting | `src/accounting/` | C# / .NET 10 | ASP.NET Core, Kafka consumer |
| ad | `src/ad/` | Java 21 | Spring Boot, gRPC |
| cart | `src/cart/` | C# / .NET 10 | ASP.NET Core, gRPC, Valkey (StackExchange.Redis) |
| checkout | `src/checkout/` | Go 1.24+ | gRPC, Sarama Kafka producer |
| currency | `src/currency/` | C++17 | gRPC, OpenTelemetry C++ SDK |
| email | `src/email/` | Ruby 3.4+ | Sinatra |
| flagd | `src/flagd/` | JSON config | flagd daemon (hot-reloaded) |
| flagd-ui | `src/flagd-ui/` | Elixir | Phoenix LiveView |
| fraud-detection | `src/fraud-detection/` | Kotlin / JDK 21 | Spring Boot, Kafka consumer |
| frontend | `src/frontend/` | TypeScript / Node.js 20+ | Next.js 14 (Pages Router), React 18, styled-components v6 |
| frontend-proxy | `src/frontend-proxy/` | Envoy YAML config | Envoy proxy |
| image-provider | `src/image-provider/` | nginx config | ngx_otel_module |
| kafka | `src/kafka/` | Kafka KRaft config | Java-based broker |
| llm | `src/llm/` | Python 3.11+ | Flask |
| load-generator | `src/load-generator/` | Python 3.11+ | Locust + Playwright |
| otel-collector | `src/otel-collector/` | YAML config | OpenTelemetry Collector Contrib |
| payment | `src/payment/` | JavaScript / Node.js 20+ | gRPC (`@grpc/proto-loader`) |
| product-catalog | `src/product-catalog/` | Go 1.24+ | gRPC, PostgreSQL |
| product-reviews | `src/product-reviews/` | Python 3.11+ | gRPC, OpenAI client |
| prometheus | `src/prometheus/` | YAML config | Prometheus |
| quote | `src/quote/` | PHP 8.4 | Slim Framework |
| recommendation | `src/recommendation/` | Python 3.11+ | gRPC |
| shipping | `src/shipping/` | Rust (latest stable) | Actix-web |

## Language Knowledge Files

| File | Languages / Runtimes Covered |
|---|---|
| `go.md` | Go (checkout, product-catalog) |
| `python.md` | Python (llm, load-generator, product-reviews, recommendation) |
| `dotnet.md` | C#/.NET (accounting, cart) |
| `java-kotlin.md` | Java (ad), Kotlin (fraud-detection), Kafka config |
| `nodejs.md` | JavaScript/Node.js (payment) |
| `typescript-nextjs.md` | TypeScript/Next.js (frontend) |
| `rust.md` | Rust (shipping) |
| `ruby.md` | Ruby (email) |
| `php.md` | PHP (quote) |
| `cpp.md` | C++ (currency) |
| `infra-config.md` | flagd, Envoy, nginx, OTel Collector, Prometheus, Grafana, Kafka config, PostgreSQL, OpenSearch |

## Proto Contracts

A single proto file (`pb/demo.proto`) defines all service interfaces. Generated
stubs exist for multiple languages:

| Language | Generated Location | Regeneration Command |
|---|---|---|
| Go | `src/checkout/genproto/`, `src/product-catalog/genproto/` | `make docker-generate-protobuf` |
| Python | `src/recommendation/demo_pb2*.py`, `src/product-reviews/demo_pb2*.py` | `make docker-generate-protobuf` |
| TypeScript | `src/frontend/protos/demo.ts` | `make docker-generate-protobuf` |
| C++ | `src/currency/build/generated/proto/` | `make docker-generate-protobuf` |

**Rule:** Never hand-edit generated files. Always regenerate via
`make docker-generate-protobuf` after changing `pb/demo.proto`.

## Test Infrastructure

| Test Type | Location | Run Command |
|---|---|---|
| Trace-based (Tracetest) | `test/tracetesting/` | `make run-tracetesting` |
| Integration / unit | Per-service (see language files) | `make run-tests` |

## Out-of-Scope: react-native-app

`src/react-native-app/` is a TypeScript/React Native + Expo mobile app example.
It is **out of scope** for the SDD workshop:

- No domain expert agent covers it.
- No implementer agent is assigned to it.
- No language knowledge file exists for it.
- It is not part of the core service mesh (no gRPC, no Kafka,
  no OTel Collector pipeline).

Treat it as read-only reference material. Do not add it to agent routing
or assign it to an implementer without explicit user approval.
