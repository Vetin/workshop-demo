# jaeger

## Identity

- **Language**: N/A
- **Framework**: Jaeger 2.12.0
- **Ports**: 16686 (`JAEGER_UI_PORT`, web UI), 4317 (`JAEGER_GRPC_PORT`, OTLP gRPC intake)
- **Dockerfile**: None — uses upstream `${JAEGERTRACING_IMAGE}`
- **Main entry point**: `src/jaeger/config.yml`

## Responsibility

Distributed trace storage and visualization. Receives traces from otel-collector. Provides the Jaeger UI accessible through frontend-proxy at `/jaeger/`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| otel-collector | OTLP | Receives traces exported by collector |
| prometheus | HTTP | Metrics backend for Jaeger's own metrics |

## Key Source Files

- `src/jaeger/config.yml` — Jaeger v2 configuration (storage, query, collector settings)

## Risky Notes

Jaeger is configured with `MEMORY_MAX_TRACES=25000`. Once this limit is reached, old traces are evicted. In long workshop sessions, early traces will disappear from the UI.
