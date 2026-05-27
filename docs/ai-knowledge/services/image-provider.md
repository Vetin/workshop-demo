# image-provider

## Identity

- **Language**: N/A
- **Framework**: nginx with `ngx_otel_module`
- **Port**: 8081 (`IMAGE_PROVIDER_PORT`)
- **Dockerfile**: `src/image-provider/Dockerfile`
- **Main entry point**: `src/image-provider/nginx.conf.template`

## Responsibility

Serves static product images. Accessed via frontend-proxy at path prefix `/images/`. No dynamic logic — pure static file server with OTel tracing.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| otel-collector | gRPC | Export nginx traces |

Environment variables: `IMAGE_PROVIDER_PORT`, `OTEL_COLLECTOR_HOST`, `OTEL_COLLECTOR_PORT_GRPC`, `OTEL_SERVICE_NAME`.

## OTel Instrumentation

- **Approach**: `ngx_otel_module` loaded as a dynamic module (`load_module modules/ngx_otel_module.so`).
- Config in `src/image-provider/nginx.conf.template` lines 1–17:
  - `otel_exporter { endpoint ${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_GRPC}; }` — gRPC export.
  - `otel_trace on` — traces all requests.
  - `otel_trace_context propagate` — reads and propagates W3C trace context.
- A `/status` endpoint (line 35) is scraped by the otel-collector `nginx` receiver.

## Key Source Files

- `src/image-provider/nginx.conf.template` — full nginx config
- `src/image-provider/static/` — static image files
- `src/image-provider/Dockerfile`

## Risky Notes

The nginx config is a template rendered with `envsubst` at container start. Missing env vars silently produce a broken nginx config. The `ngx_otel_module.so` must be compiled for the exact nginx version in the base image.
