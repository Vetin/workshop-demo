# Observability Detail

Per-service instrumentation patterns, custom spans, custom metrics, logging approaches, semantic conventions, trace-based tests, and the rules for keeping telemetry up to date when features change.

---

## Collector configuration reference

**Primary config:** `src/otel-collector/otelcol-config.yml`
**Extras stub:** `src/otel-collector/otelcol-config-extras.yml`
**Test override:** `test/tracetesting/otelcol-config-tracetest.yml`

The test override uses `otelcol-config.yml` as a base and merges the test config on top via docker-compose. It removes the `transform` and `memory_limiter` processors from the traces pipeline and adds an `otlp/tracetest` exporter pointing to `tracetest-server:4317`.

The collector's own telemetry (self-monitoring) is exported via OTLP HTTP back to itself:
- Metrics: periodic reader → `http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`
- Logs: batch processor → same endpoint

---

## Telemetry schema / protobuf location

`pb/demo.proto` — single canonical proto file that defines all RPC service contracts. Each service generates language-specific stubs from it. The file is the ground truth for what operation names appear in traces (e.g., `oteldemo.CheckoutService/PlaceOrder`).

Generated stubs live alongside source:
- Go: `src/checkout/genproto/oteldemo/`, `src/product-catalog/genproto/oteldemo/`
- Python: `src/recommendation/demo_pb2*.py`, `src/product-reviews/demo_pb2*.py`
- TypeScript: `src/frontend/protos/demo.ts`
- C++: `src/currency/build/generated/proto/`

---

## Per-service instrumentation

### ad (Java, `src/ad/`)

**SDK init:** Uses `GlobalOpenTelemetry` — the Java agent (injected at container startup) initialises the SDK. No manual provider setup in application code.

**Tracer name:** `"ad"` (via `GlobalOpenTelemetry.getTracer("ad")`)

**Custom spans:**
- `getAdsByCategory` — created with `@WithSpan` annotation; category passed as `@SpanAttribute("app.ads.category")`.
- `getRandomAds` — created manually via `tracer.spanBuilder("getRandomAds").startSpan()`.
- The gRPC handler `getAds` adds attributes to the auto-instrumented span.

**Custom span attributes:**
- `app.ads.contextKeys` — stringified list of requested context keys
- `app.ads.contextKeys.count` — count
- `app.ads.count` — number of ads returned
- `app.ads.ad_request_type` — `TARGETED` or `NOT_TARGETED`
- `app.ads.ad_response_type` — `TARGETED` or `RANDOM`
- `session.id` — read from W3C baggage entry `session.id`

**Custom metrics:**
- `app.ads.ad_requests` (counter) — dimensions: `app.ads.ad_request_type`, `app.ads.ad_response_type`

**Logging:** Log4j2 with `log4j2.xml` at `src/fraud-detection/src/main/resources/log4j2.xml` (same pattern used in ad); logs emitted to OTLP via the Java agent's log bridge.

**Feature flag hooks:** FlagdProvider built with `withGlobalTelemetry(true)` — flag evaluation decisions appear as child spans automatically.

---

### cart (.NET/C#, `src/cart/`)

**SDK init:** `src/cart/src/Program.cs`
- Tracing: `AddSource("OpenTelemetry.Demo.Cart")`, Redis instrumentation (`SetVerboseDatabaseStatements = true`), ASP.NET Core, gRPC client, HTTP client, OTLP exporter.
- Metrics: meter `"OpenTelemetry.Demo.Cart"` + `"OpenFeature"`, Process/Runtime/ASP.NET Core instrumentation, `ExemplarFilterType.TraceBased`, OTLP exporter.
- Logging: `.AddOpenTelemetry(options => options.AddOtlpExporter())` + console.

**ActivitySource:** `"OpenTelemetry.Demo.Cart"` (defined in `ValkeyCartStore.cs`)

**Custom span attributes** (set on auto-instrumented gRPC activity in `CartService.cs`):
- `app.user.id`, `app.product.id`, `app.product.quantity` (on `AddItem`)
- `app.user.id`, `app.cart.items.count` (on `GetCart`)
- `app.user.id` (on `EmptyCart`)

**Custom metrics** (`src/cart/src/cartstore/ValkeyCartStore.cs`):
- `app.cart.add_item.latency` (histogram, seconds) — custom bucket boundaries `[0.005 … 10]`
- `app.cart.get_cart.latency` (histogram, seconds) — same boundaries

**Feature flag:** `cartFailure` — when enabled, `EmptyCart` is routed to `badhost:1234`, generating a Redis connection error recorded on the span.

---

### checkout (Go, `src/checkout/`)

**SDK init:** `src/checkout/main.go` — manual setup of three providers.
- Trace: `otlptracegrpc.New` + `sdktrace.WithBatcher` + resource detectors (`WithOS`, `WithProcess`, `WithContainer`, `WithHost`).
- Metrics: `otlpmetricgrpc.New` + `sdkmetric.NewPeriodicReader`.
- Logs: `otlploggrpc.New` + `sdklog.NewBatchProcessor` + `global.SetLoggerProvider`.
- `runtime.Start` for Go runtime metrics.
- gRPC server: `otelgrpc.NewServerHandler()`.
- gRPC clients: `otelgrpc.NewClientHandler()`.
- HTTP client calls use `otelhttp.Post`.

**Tracer name:** `"checkout"`

**Propagation:** W3C TraceContext + W3C Baggage.

**Custom span attributes** on `PlaceOrder` gRPC handler span:
- `app.user.id`, `app.user.currency`
- `app.order.id`, `app.order.amount`, `app.order.items.count`
- `app.shipping.amount`, `app.shipping.tracking.id`
- `app.order.gift_wrap` (bool) — set on every `PlaceOrder` span regardless of selection (`src/checkout/main.go:296`)
- `app.order.gift_wrap.amount` (float64) — set only when `gift_wrap=true`; value is the $5 USD fee converted to user currency (`src/checkout/main.go:359`)

On `prepareOrderItemsAndShippingQuoteFromCart` child span:
- `app.shipping.amount`, `app.cart.items.count`, `app.order.items.count`

**Span events:**
- `"prepared"` — after cart/product/shipping retrieval
- `"charged"` — after payment, with attribute `app.payment.transaction.id`
- `"shipped"` — after shipping, with attribute `app.shipping.tracking.id`
- `"gift_wrap_fee_applied"` — emitted only when `gift_wrap=true`, after currency conversion of the $5 fee (`src/checkout/main.go:348`)
- `"error"` on deferred error handler — with `exception.message`

**Kafka producer span** (`createProducerSpan`):
- SpanKind: `Producer`
- Attributes: `peer.service=kafka`, `network.transport=tcp`, `messaging.system=kafka`, `messaging.destination.name=orders`, `messaging.operation=publish`, `messaging.kafka.destination.partition`
- After success/failure: `messaging.kafka.producer.success`, `messaging.kafka.producer.duration_ms`, `messaging.kafka.message.offset`
- Propagation injected into Kafka message headers.

**Logging:** `otelslog.NewLogger("checkout")` — structured slog with OTLP bridge. Log fields mirror span attributes (`app.order.id`, `app.order.amount`, etc.).

**OpenFeature hooks:** `otelhooks.NewTracesHook()` — flag evaluations appear as child spans.

---

### currency (C++, `src/currency/`)

**SDK init:** `src/currency/src/tracer_common.h`, `src/currency/src/meter_common.h`, `src/currency/src/logger_common.h`
- Tracer: `OtlpGrpcExporterFactory::Create` + `SimpleSpanProcessorFactory`.
- Meter: `OtlpGrpcMetricExporterFactory` + `PeriodicExportingMetricReader`.
- Propagator: `HttpTraceContext`.

**Custom spans** (manual) in `src/currency/src/server.cpp`:
- `Currency/GetSupportedCurrencies` (SERVER kind) — events: `"Processing supported currencies request"`, `"Currencies fetched, response sent back"`
- `Currency/Convert` (SERVER kind) — attributes: `app.currency.conversion.from`, `app.currency.conversion.to`

**Custom metrics:**
- A counter created via `initIntCounter` in `meter_common.h` (name derived at runtime from the meter name).

---

### email (Ruby/Sinatra, `src/email/`)

**SDK init:** `src/email/email_server.rb`
- `OpenTelemetry::SDK.configure` with Sinatra instrumentation.
- Logger: `OpenTelemetry.logger_provider.logger(name: 'email')`.
- Metrics: OTLP metrics exporter added to meter provider.

**Custom span:** `send_email` — manually created child span inside `send_email` method.

**Custom span attributes:**

- `app.order.id` — added to auto-instrumented Sinatra span on `POST /send_order_confirmation` (`email_server.rb:50`)
- `app.email.recipient` — added to the `send_email` child span (`email_server.rb:88`)

**Custom metric:**
- `app.confirmation.counter` (counter, unit: `"1"`) — incremented for each order confirmation email.

**Feature flag:** `emailMemoryLeak` — multiplier applied to email body padding inside `send_email` span.

---

### fraud-detection (Kotlin/JVM, `src/fraud-detection/`)

**SDK init:** Java agent injection (no manual SDK code). FlagdProvider with `withGlobalTelemetry(true)`.

**Telemetry:** Only auto-instrumented spans from Kafka consumer. Log4j2 for logging.

**Feature flag:** `kafkaQueueProblems` — when > 0, adds a 1-second sleep per consumed message inside the consumer loop.

---

### frontend (Next.js SSR, `src/frontend/`)

**Server-side SDK init:** `src/frontend/utils/telemetry/Instrumentation.js`
- `NodeSDK` with `getNodeAutoInstrumentations` (fs instrumentation disabled).
- OTLP gRPC exporters for traces and metrics.
- Resource detectors: container, env, host, os, process, Alibaba, AWS, GCP.

**Browser-side SDK init:** `src/frontend/utils/telemetry/FrontendTracer.ts`
- `WebTracerProvider` with `BatchSpanProcessor` → `OTLPTraceExporter` (HTTP to `NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`).
- `SessionIdProcessor` — adds `session.id` to every browser span.
- Auto-instrumentations: `getWebAutoInstrumentations` with fetch instrumentation that propagates trace headers to all origins and adds `app.synthetic_request`.

**Service names:**
- Server-side: `frontend` (env `OTEL_SERVICE_NAME=frontend`)
- Browser: `frontend-web` (env `WEB_OTEL_SERVICE_NAME=frontend-web`)

**InstrumentationMiddleware** (`src/frontend/utils/telemetry/InstrumentationMiddleware.ts`):
- Wraps every Next.js API route handler.
- Increments `app.frontend.requests` counter (dimensions: `method`, `target`, `status`).
- Sets `http.status_code` on the active span.
- Records exceptions and sets span status ERROR on failure.

**SessionIdProcessor** (`src/frontend/utils/telemetry/SessionIdProcessor.ts`):
- `onStart` adds `session.id` (value: `userId` from `SessionGateway.getSession()`) to every browser span.

**Attribute name enum:** `src/frontend/utils/enums/AttributeNames.ts` defines `SESSION_ID = 'session.id'`.

---

### payment (Node.js, `src/payment/`)

**SDK init:** `src/payment/opentelemetry.js`
- `NodeSDK` with `getNodeAutoInstrumentations` (fs only when parent span exists).
- `RuntimeNodeInstrumentation` at 5000 ms precision.
- OTLP gRPC exporters.
- Same cloud resource detectors as frontend.

**Tracer name:** `"payment"`

**Custom span:** `charge` — manually started and ended inside `charge()`.

**Custom span attributes:**
- `app.payment.card_type`, `app.payment.card_valid`
- `app.loyalty.level` (random from `['platinum', 'gold', 'silver', 'bronze']`)
- `app.payment.charged` (true/false based on `synthetic_request` baggage)

**Custom metric:**
- `app.payment.transactions` (counter) — dimension: `app.payment.currency`

**Logging:** `src/payment/logger.js` — pino with `pino-opentelemetry-transport`, batch OTLP gRPC exporter + console simple exporter. Logger name: `payment-logger`. Mixes in `service.name` from `OTEL_SERVICE_NAME`.

**Feature flag:** `paymentFailure` — numeric probability (0–1). When triggered, sets `app.loyalty.level=gold` on span before throwing.

---

### product-catalog (Go, `src/product-catalog/`)

**SDK init:** Same three-provider pattern as checkout (trace/metric/log via OTLP gRPC).

**Database instrumentation:**
- `otelsql.Open` wraps the `database/sql` driver with `semconv.DBSystemNamePostgreSQL`, span options `OmitConnResetSession: true, OmitRows: true`.
- `otelsql.RegisterDBStatsMetrics` — auto-emits DB connection pool metrics.

**Custom span attributes:**
- `ListProducts` → `app.products.count`
- `GetProduct` → `app.product.id`, `app.product.name`; event `"Product Found"`; status ERROR on failure or feature flag
- `SearchProducts` → `app.products_search.count`

**Feature flag:** `productCatalogFailure` — fails GetProduct for product ID `OLJCESPC7Z` with span status ERROR.

---

### product-reviews (Python, `src/product-reviews/`)

**SDK init:** Manual (`opentelemetry` SDK), OTLP gRPC log exporter with `BatchLogRecordProcessor`, custom JSON logger pattern.

**Custom metrics** (`src/product-reviews/metrics.py`):
- `app_product_review_counter` (counter, unit: `reviews`)
- `app_ai_assistant_counter` (counter, unit: `summaries`)

**LLM integration:** Uses `openai` Python client pointed at the local `llm` service. Tool calls (`fetch_product_reviews`) generate child spans via OpenAI SDK instrumentation.

---

### quote (PHP/Slim, `src/quote/`)

**SDK init:** Relies on `OTEL_*` environment variables; Slim auto-instrumentation.

**Custom span:** `calculate-quote` (SpanKind INTERNAL) — manually created inside `calculateQuote()`.

**Custom span attributes:**
- `app.quote.items.count`, `app.quote.cost.total`

**Span events:** `"Calculating quote"`, `"Quote calculated, returning its value"`

**Custom metric:**
- `quotes` (counter, unit: `quotes`) — dimension: `number_of_items`

**Logging:** Monolog with `OpenTelemetry\Contrib\Logs\Monolog\Handler` — logs bridge to OTLP.

---

### recommendation (Python, `src/recommendation/`)

**SDK init:** Manual, OTLP gRPC log exporter. Tracer and meter obtained from global providers configured via env vars.

**Custom span:** `get_product_list` — `tracer.start_as_current_span("get_product_list")`.

**Custom span attributes:**
- `app.recommendation.cache_enabled`, `app.cache_hit`
- `app.products.count`, `app.filtered_products.count`
- `app.filtered_products.list`, `app.products_recommended.count`

**Custom metric** (`src/recommendation/metrics.py`):
- `app_recommendations_counter` (counter, unit: `recommendations`) — dimension: `recommendation.type`

**Logging:** Custom `CustomJsonFormatter` (`logger.py`) embeds `otelTraceID` and `otelSpanID` into every JSON log line.

**Feature flag:** `recommendationCacheFailure` — enables cache-leak simulation path.

---

### shipping (Rust, `src/shipping/`)

**SDK init:** `src/shipping/src/telemetry_conf.rs` — `pub fn init_otel()` initialises logger, tracer, and meter providers via OTLP tonic (gRPC). Resource detectors: `OsResourceDetector`, `ProcessResourceDetector`. Uses `opentelemetry_appender_tracing` bridge so `tracing` crate events flow to OTLP logs. Propagator: `TraceContextPropagator`.

**Spans:** Auto-instrumented via actix-web middleware. Structured log events in `shipping_service.rs` using the `tracing` crate:
- `info!(name = "SendingQuoteValue", quote.dollars, quote.cents, message = "Sending Quote")`
- `info!(name = "CreatingTrackingId", tracking_id, message = "Tracking ID Created")`

No app-prefixed custom attributes in shipping.

---

### accounting (.NET/C#, `src/accounting/`)

**SDK init:** Host builder with `AddOpenTelemetry` (implicit from `Directory.Build.props` and package refs). Tracing via `ActivitySource("Accounting.Consumer")`.

**Custom span:** `order-consumed` (ActivityKind.Internal) — started for each Kafka message.

**Logging:** `ILogger` with structured log: `Log.OrderReceivedMessage(_logger, order)`.

---

### frontend-proxy (Envoy, `src/frontend-proxy/`)

Envoy is configured with `envoy.tracers.opentelemetry` in `envoy.tmpl.yaml` with `spawn_upstream_span: true`. This generates parent spans for all inbound HTTP/gRPC requests and propagates context downstream. No custom application attributes — all spans are standard Envoy HTTP/gRPC spans.

---

## Semantic conventions

All services follow OTel semantic conventions. Key namespaces in use:

| Namespace | Used by |
|-----------|---------|
| `service.*` | All services (via SDK resource, `service.name` set via `OTEL_SERVICE_NAME`) |
| `http.*` | Frontend, shipping, frontend-proxy (auto) |
| `rpc.*` | All gRPC services (auto via `otelgrpc`) |
| `messaging.*` | Checkout Kafka producer (`messaging.system=kafka`, `messaging.destination.name`, `messaging.operation`, `messaging.kafka.message.offset`) |
| `db.*` | Product-catalog (`db.system=postgresql` via `otelsql`) |
| `exception.*` | Checkout (`semconv.ExceptionMessageKey`), ad, cart |
| `peer.service` | Checkout Kafka span (`peer.service=kafka`) |
| `network.transport` | Checkout Kafka span (`tcp`) |
| `process.*` | Go runtime (`runtime.Start`), Node.js runtime instrumentation |
| `browser.*` | Frontend-web (browser detector) |

Checkout uses `semconv/v1.24.0`. Product-catalog uses `semconv/v1.38.0`. The versions differ — keep this in mind when adding new attributes.

---

## Manual span patterns

Three patterns appear across the codebase:

**Pattern 1 — Annotate the auto-instrumented span (most common)**
```go
// Go (checkout, product-catalog)
span := trace.SpanFromContext(ctx)
span.SetAttributes(attribute.String("app.user.id", req.UserId))
span.AddEvent("prepared")
```

**Pattern 2 — Start a new child span manually**
```go
// Go (checkout)
ctx, span := tracer.Start(ctx, "prepareOrderItemsAndShippingQuoteFromCart")
defer span.End()
```
```java
// Java (ad)
Span span = tracer.spanBuilder("getRandomAds").startSpan();
try (Scope ignored = span.makeCurrent()) { ... } finally { span.end(); }
```
```ruby
# Ruby (email)
tracer.in_span("send_email") do |span| ... end
```

**Pattern 3 — WithSpan annotation (Java)**
```java
@WithSpan("getAdsByCategory")
private Collection<Ad> getAdsByCategory(@SpanAttribute("app.ads.category") String category) { ... }
```

---

## Metrics patterns

Custom metrics follow a consistent naming convention: `app.<service>.<operation>` or `app.<domain>.<metric>`.

| Metric | Type | Service | Dimensions |
|--------|------|---------|-----------|
| `app.ads.ad_requests` | counter | ad | `app.ads.ad_request_type`, `app.ads.ad_response_type` |
| `app.cart.add_item.latency` | histogram (s) | cart | — |
| `app.cart.get_cart.latency` | histogram (s) | cart | — |
| `app.confirmation.counter` | counter | email | — |
| `app.frontend.requests` | counter | frontend | `method`, `target`, `status` |
| `app.payment.transactions` | counter | payment | `app.payment.currency` |
| `app_recommendations_counter` | counter | recommendation | `recommendation.type` |
| `app_product_review_counter` | counter | product-reviews | — |
| `app_ai_assistant_counter` | counter | product-reviews | — |
| `quotes` | counter | quote | `number_of_items` |
| spanmetrics-derived | histogram+counter | collector | auto from traces |
| DB pool stats | gauge | product-catalog | `db.system` |
| Runtime metrics | various | Go/Node/Python services | auto |

---

## Structured logging patterns

| Runtime | Approach |
|---------|---------|
| Go (checkout, product-catalog) | `otelslog.NewLogger` from `go.opentelemetry.io/contrib/bridges/otelslog`; log fields mirror span attributes |
| Python (recommendation) | Custom `CustomJsonFormatter` embeds `otelTraceID` and `otelSpanID` in every JSON line |
| Node.js (payment) | pino + `pino-opentelemetry-transport`, batch OTLP gRPC |
| Node.js (frontend server) | NodeSDK auto-instrumentation picks up console logs |
| Ruby (email) | OpenTelemetry logger provider directly; OTLP exporter |
| PHP (quote) | Monolog + OpenTelemetry Monolog Handler |
| .NET (cart, accounting) | `ILogger` + `AddOpenTelemetry()` OTLP exporter |
| Java (ad, fraud-detection) | Log4j2 + Java agent OTLP log bridge |
| Rust (shipping) | `tracing` crate + `opentelemetry_appender_tracing` bridge |

All logs end up in OpenSearch under the index pattern `otel-logs-{yyyy-MM-dd}`. Grafana OpenSearch datasource (`webstore-logs`) uses `body` as message field, `severity.text.keyword` as level field, and `observedTimestamp` as time field.

---

## Trace-based test entry points

Tests live in `test/tracetesting/`. Each test is a Tracetest YAML file that triggers a real call and then asserts against the resulting distributed trace.

| Directory | Tests |
|-----------|-------|
| `ad/` | `get.yaml` — GetAds gRPC |
| `cart/` | add item, check empty/populated, empty cart |
| `checkout/` | add item to cart, place order (full end-to-end gRPC) |
| `currency/` | convert, list supported currencies |
| `email/` | send confirmation |
| `frontend/` | 01 see ads → 02 recommendations → 03 browse product → 04 add to cart → 05 view cart → 06 checkout (HTTP to `/api/checkout`) |
| `payment/` | valid card, invalid card, expired card, Amex not allowed |
| `product-catalog/` | get, list, search |
| `product-reviews/` | reviews, summary |
| `recommendation/` | list recommendations |
| `shipping/` | get-quote (empty + populated), ship order |

Test assertions reference both RPC-level attributes (`rpc.grpc.status_code`, `rpc.method`) and custom `app.*` attributes (e.g., `app.user.id`, `app.order.items.count`). The full e2e checkout test (`frontend/06-checking-out-cart.yaml`) asserts:
- `app.user.id`, `app.order.items.count` on the PlaceOrder span
- `rpc.grpc.status_code = 0` on the PaymentService/Charge span
- `http.response.status_code = 200` on `/ship-order`
- `messaging.destination.name = "orders"` on the Kafka producer span

**Test collector config:** `test/tracetesting/otelcol-config-tracetest.yml` — the traces pipeline exports to `tracetest-server:4317` without transform or memory_limiter processors. Tracetest itself is configured in `test/tracetesting/tracetest-config.yaml` and exports its own telemetry to `otel-collector:4317`.

---

## Sensitive data rules

1. **Credit card numbers** must never appear in span attributes, metric labels, or structured log fields. Only `app.payment.card_type` and `app.payment.card_valid` are permitted as span attributes. Last-four-digits may appear in error message strings but not as dedicated attributes.
2. **CVV values** must never be logged or attributed anywhere in the pipeline.
3. **Email addresses** must not be span attributes. Free-form log messages that incidentally include email addresses (e.g., checkout `logger.Warn`) are acceptable but discouraged for new code.
4. **User IDs** (`app.user.id`, `session.id`) are UUID session identifiers, not real-world PII. They are permitted as span attributes.
5. **The `transform` processor** at the collector strips query strings from all span names (`replace_pattern(name, "\\?.*", "")`). Any new route that might carry tokens or PII in query parameters is automatically scrubbed at ingestion. Do not bypass this processor.
6. **Baggage** is used for `session.id` and `synthetic_request`. Do not propagate PII through baggage.
7. **Log indexes** in OpenSearch (`otel-logs-*`) receive all service logs. New structured log fields that could contain PII require a risk review before adding.

---

## When feature changes should update telemetry

| Change type | Telemetry impact |
|-------------|-----------------|
| New RPC method added to `pb/demo.proto` | Trace-based tests need a new YAML in `test/tracetesting/<service>/`; the span name follows the pattern `<package>.<Service>/<Method>` |
| New business event in checkout flow | Add a `span.AddEvent(...)` call and update `test/tracetesting/checkout/place-order.yaml` assertions |
| New feature flag | Add an entry to `src/flagd/demo.flagd.json`; if it changes observable service behaviour, add/update tracetest assertions; if it affects latency or error rate, update alerting in `src/grafana/provisioning/alerting/` |
| New service added | Requires `OTEL_SERVICE_NAME` env var in `docker-compose.yml`; SDK init in the service; new entry in this document; trace-test directory under `test/tracetesting/` |
| New API endpoint on an existing service | The `transform` processor may need a new `replace_match` rule if the route has variable path segments |
| New metric added | Update the metrics table in this document; consider adding a Grafana panel or alerting rule |
| Any change to cart, checkout, or payment service logic | Re-run the full frontend trace-test suite (`test/tracetesting/frontend/all.yaml`) to verify assertion coverage |
| LLM/AI assistant behaviour change | `test/tracetesting/product-reviews/summary.yaml` covers the AI assistant path; assertions on `app_ai_assistant_counter` should be revisited |
