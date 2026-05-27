# product-catalog

## Identity

- **Language**: Go
- **Framework**: gRPC Go + PostgreSQL (`database/sql` + `lib/pq`)
- **Port**: 3550 (`PRODUCT_CATALOG_PORT`)
- **Dockerfile**: `src/product-catalog/Dockerfile`
- **Main entry point**: `src/product-catalog/main.go`

## Responsibility

Stores and retrieves product data from PostgreSQL. Exposes `ProductCatalogService` gRPC methods: `ListProducts`, `GetProduct`, `SearchProducts`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| postgresql | TCP/SQL | Product data storage |
| flagd | gRPC (OpenFeature) | Feature flags |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `PRODUCT_CATALOG_PORT`, `DB_CONNECTION_STRING`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Go SDK configured manually in `src/product-catalog/main.go`.
- **Libraries**: `otelgrpc` for gRPC server; `otelslog` bridge for structured logs; `otelsql` (`XSAM/otelsql`) for database query tracing (line 53 of main.go).
- **DB semconv**: `OTEL_SEMCONV_STABILITY_OPT_IN=database` — opts into stable database semantic conventions.
- **Exporters**: OTLP gRPC for traces, metrics, logs.
- **Runtime instrumentation**: `go.opentelemetry.io/contrib/instrumentation/runtime`.
- **OpenFeature**: `otelhooks.NewTracesHook()`.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service ProductCatalogService {
    rpc ListProducts(Empty) returns (ListProductsResponse) {}
    rpc GetProduct(GetProductRequest) returns (Product) {}
    rpc SearchProducts(SearchProductsRequest) returns (SearchProductsResponse) {}
}
```
Callers: checkout, recommendation, product-reviews, frontend.

## Key Source Files

- `src/product-catalog/main.go` — entry point, gRPC server, OTel setup, SQL queries
- `src/product-catalog/genproto/` — generated protobuf stubs
- `src/product-catalog/Dockerfile`

## Risky Notes

`OTEL_SEMCONV_STABILITY_OPT_IN=database` is set. If this env var is removed or changed, database span attribute names will revert to the unstable convention, breaking dashboards that query by the stable names.
