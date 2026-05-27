# frontend-proxy

## Identity

- **Language**: N/A
- **Framework**: Envoy Proxy
- **Ports**: 8080 (`ENVOY_PORT`, public), 10000 (`ENVOY_ADMIN_PORT`, admin)
- **Dockerfile**: `src/frontend-proxy/Dockerfile`
- **Main entry point**: `src/frontend-proxy/envoy.tmpl.yaml` (template rendered at container start)

## Responsibility

Single ingress point for all external traffic. Routes requests to: frontend, load-generator (Locust UI), otel-collector (OTLP HTTP), Jaeger UI, Grafana, image-provider, flagd, and flagd-ui. Also propagates trace context for all routed requests.

## Routing Table (from `src/frontend-proxy/envoy.tmpl.yaml`)

| Path prefix | Upstream cluster |
|---|---|
| `/loadgen/` | load-generator |
| `/otlp-http/` | otel-collector HTTP (4318) |
| `/jaeger/` | jaeger (16686) |
| `/grafana/` | grafana (3000) |
| `/images/` | image-provider (8081) |
| `/flagservice/` | flagd (8013) |
| `/feature` | flagd-ui (4000) |
| all other | frontend (8080) |

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| frontend | HTTP | Main app |
| load-generator | HTTP | Locust web UI |
| jaeger | HTTP | Trace UI |
| grafana | HTTP | Metrics UI |
| flagd-ui | HTTP | Feature flag UI |
| image-provider | HTTP | Static product images |
| otel-collector | gRPC (tracing), HTTP (OTLP proxy) | OTel export + browser OTLP relay |

## OTel Instrumentation

- **Approach**: Envoy native OpenTelemetry tracing via `envoy.tracers.opentelemetry` (envoy.tmpl.yaml lines 22–33).
- **Export**: gRPC to otel-collector cluster (`opentelemetry_collector_grpc`).
- `spawn_upstream_span: true` creates child spans for each upstream request.
- Environment resource detector reads `OTEL_RESOURCE_ATTRIBUTES`.

## Key Source Files

- `src/frontend-proxy/envoy.tmpl.yaml` — full Envoy config template
- `src/frontend-proxy/Dockerfile`

## Risky Notes

The Envoy config is a Go template rendered at startup. If any referenced environment variable is missing, the rendered config will contain literal `${VAR}` strings that will cause Envoy to fail. The variables `ENVOY_ADDR`, `ENVOY_PORT`, `FRONTEND_HOST`, `FRONTEND_PORT` are all required.
