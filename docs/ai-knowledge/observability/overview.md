# Observability Overview

This document summarizes the observability architecture of the OpenTelemetry Demo. All services emit traces, metrics, and logs to a central OTel Collector, which fans out to Jaeger (traces), Prometheus (metrics), and OpenSearch (logs). Grafana provides unified dashboards and alerting.

## Signal flow

```
Services (OTLP gRPC or HTTP)
  --> OTel Collector (src/otel-collector/otelcol-config.yml)
        |-- traces  --> Jaeger (port 4317)
        |               also fed to spanmetrics connector
        |-- metrics --> Prometheus (http://prometheus:9090/api/v1/otlp)
        |               sources: OTLP + docker_stats + hostmetrics + nginx + postgresql + redis
        `-- logs    --> OpenSearch (index: otel-logs-*)
```

Browser/frontend-web spans go via OTLP HTTP (`/v1/traces`) through the Envoy proxy to the collector.

## Collector config locations

| File | Purpose |
|------|---------|
| `src/otel-collector/otelcol-config.yml` | Primary config: receivers, processors, exporters, pipelines |
| `src/otel-collector/otelcol-config-extras.yml` | User-extension stub (currently empty example) |
| `test/tracetesting/otelcol-config-tracetest.yml` | Trace-test override: adds `otlp/tracetest` exporter, strips processors from traces pipeline |

## Receivers

| Receiver | What it collects |
|----------|-----------------|
| `otlp` (gRPC + HTTP with CORS) | All application telemetry |
| `httpcheck/frontend-proxy` | Availability check on Envoy |
| `nginx` | NGINX metrics from image-provider (10 s interval) |
| `docker_stats` | Container CPU/memory/network/io via Docker socket |
| `postgresql` | 8 explicit DB metrics (blks_hit, blks_read, tuples, deadlocks) |
| `redis` | Valkey/Redis metrics (10 s interval, host: `valkey-cart:6379`) |
| `hostmetrics` | CPU, disk, load, filesystem, memory, network, paging, processes, uptime (scraped from `/hostfs`) |

## Processors

| Processor | Config |
|-----------|--------|
| `memory_limiter` | 80 % soft limit, 25 % spike; checked every 5 s |
| `resourcedetection` | Detectors: `env`, `docker`, `system` — enriches spans/metrics with host/container resource attributes |
| `transform` | Traces only: strips query strings from span names (`replace_pattern(name, "\\?.*", "")`); normalises product-ID routes (`GET /api/products/*` → `GET /api/products/{productId}`) |

## Connectors

| Connector | Purpose |
|-----------|---------|
| `spanmetrics` | Derives RED metrics (request count, error rate, duration histogram) from traces; output goes into the metrics pipeline |

## Exporters

| Exporter | Destination | Used by pipeline |
|----------|-------------|-----------------|
| `otlp` | `jaeger:4317` (insecure) | traces |
| `otlphttp/prometheus` | `http://prometheus:9090/api/v1/otlp` | metrics |
| `opensearch` | `http://opensearch:9200`, index `otel-logs-{yyyy-MM-dd}` | logs |
| `debug` | Collector stdout | all three |

## Pipelines

```
traces:   receivers=[otlp]       processors=[resourcedetection, memory_limiter, transform]  exporters=[otlp, debug, spanmetrics]
metrics:  receivers=[docker_stats, httpcheck/frontend-proxy, hostmetrics, nginx, otlp, postgresql, redis, spanmetrics]
                                  processors=[resourcedetection, memory_limiter]             exporters=[otlphttp/prometheus, debug]
logs:     receivers=[otlp]       processors=[resourcedetection, memory_limiter]             exporters=[opensearch, debug]
```

## Grafana dashboards

All dashboards are provisioned from `src/grafana/provisioning/dashboards/demo/`.

| File | Dashboard |
|------|-----------|
| `demo-dashboard.json` | Main OpenTelemetry Demo overview |
| `apm-dashboard.json` | APM — per-service RED metrics from spanmetrics |
| `spanmetrics-dashboard.json` | Spanmetrics detail |
| `exemplars-dashboard.json` | Trace exemplar linking between Prometheus and Jaeger |
| `opentelemetry-collector.json` | Collector self-monitoring |
| `NGINX-metrics.json` | NGINX/image-provider metrics |
| `postgresql-dashboard.json` | PostgreSQL DB stats |
| `linux-dashboard.json` | Host metrics (CPU, memory, disk) |

Data sources: Prometheus (`webstore-metrics`), Jaeger (`webstore-traces`), OpenSearch (`webstore-logs`).

Exemplars from Prometheus link to Jaeger traces via `trace_id`. Jaeger drill-down from a trace links to OpenSearch logs using `traceId` + `spanId` query.

## Alerting

`src/grafana/provisioning/alerting/cart-service-alerting.yml` — fires when the p95 latency for `POST /oteldemo.CartService/AddItem` exceeds a threshold for 1 minute (keeps firing for 2 min). References metric `http_server_request_duration_seconds_bucket`.

`src/grafana/provisioning/alerting/opentelemetry-collector-rules.yaml` — collector health rules.

## Service map (Jaeger topology)

Jaeger builds its service map from the `service.name` resource attribute set in each service, combined with downstream `peer.service` / span relationship data. The full service graph:

```
load-generator
  -> frontend (Next.js SSR + browser)
       -> frontend-proxy (Envoy)
             -> ad             (gRPC)
             -> cart           (gRPC -> valkey-cart)
             -> checkout       (gRPC)
             -> currency       (gRPC)
             -> product-catalog (gRPC -> PostgreSQL)
             -> product-reviews (gRPC -> PostgreSQL)
             -> recommendation (gRPC)
             -> shipping       (HTTP)
             -> quote          (HTTP)
  checkout
    -> payment   (gRPC)
    -> email     (HTTP)
    -> shipping  (HTTP)
    -> kafka (orders topic)
         -> accounting   (Kafka consumer, .NET)
         -> fraud-detection (Kafka consumer, Kotlin)
  product-reviews -> llm  (HTTP OpenAI-compatible)
  flagd                   (feature flag provider, contacted by all services)
```

## Feature flags (flagd)

Defined in `src/flagd/demo.flagd.json`. Flags that directly alter telemetry signal or service behaviour observable in traces:

| Flag | Service | Effect |
|------|---------|--------|
| `adFailure` | ad | 10 % chance of `UNAVAILABLE`, sets span status ERROR |
| `adManualGc` | ad | Triggers full GC (JVM GC metrics spike) |
| `adHighCpu` | ad | Runs busy-loop (CPU metrics spike) |
| `cartFailure` | cart | Routes `EmptyCart` to bad store host, span records exception |
| `paymentFailure` | payment | Configurable % chance of payment failure span |
| `paymentUnreachable` | checkout | Redirects payment gRPC to bad address |
| `recommendationCacheFailure` | recommendation | Enables cache-leak path; adds `app.cache_hit` span attribute |
| `productCatalogFailure` | product-catalog | Fails `GetProduct` for product `OLJCESPC7Z` |
| `kafkaQueueProblems` | checkout + fraud-detection | Overloads Kafka; sleep added in consumer |
| `emailMemoryLeak` | email | Pads email body; `emailMemoryLeak` multiplier in `send_email` span |
| `llmInaccurateResponse` | llm + product-reviews | Returns bad summary for product `L9ECAV7KIM` |
| `llmRateLimitError` | llm | Returns HTTP 429 |
| `loadGeneratorFloodHomepage` | load-generator | High request volume |
| `imageSlowLoad` | frontend | Delays image serving |
| `failedReadinessProbe` | cart | Breaks readiness health check |

## Sensitive data rules

The following rules apply throughout:

1. **Credit card numbers are never placed in span attributes or log fields.** In payment, only `app.payment.card_type` and `app.payment.card_valid` are recorded. `lastFourDigits` appears only in error message text and the structured log body (`logger.info`), not as a dedicated span attribute.
2. **Email addresses do not appear as span attributes.** Checkout logs warn/info messages that embed the email string in free-form text (`"order confirmation email sent to %q"`), but this is not a span attribute.
3. **User IDs** (`app.user.id`) are session-scoped UUIDs, not PII-linked identifiers.
4. **No CVV or full card number ever flows into any span, metric, or log field.**
5. The `transform` processor strips query strings from span names, preventing accidental leakage of query parameters (e.g., search terms, tokens) into Jaeger.
6. **Gift message text (`gift_message` / `giftMessage`) is PII and must never
   appear as a span attribute, event, log field, metric label, or in any OTLP
   export across any service.** Checkout passes it to the email service only
   over HTTP and never records it in telemetry. The email service renders it
   in the confirmation template only.
