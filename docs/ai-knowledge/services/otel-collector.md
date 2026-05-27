# otel-collector

## Identity

- **Language**: N/A
- **Framework**: OpenTelemetry Collector Contrib 0.142.0
- **Ports**: 4317 (`OTEL_COLLECTOR_PORT_GRPC`), 4318 (`OTEL_COLLECTOR_PORT_HTTP`)
- **Dockerfile**: None — uses upstream `${COLLECTOR_CONTRIB_IMAGE}`
- **Main entry point**: `src/otel-collector/otelcol-config.yml` (primary config), `src/otel-collector/otelcol-config-extras.yml` (override/extension config)

## Responsibility

Central telemetry pipeline. Receives all OTLP signals (traces, metrics, logs) from every instrumented service, then exports to Jaeger (traces), Prometheus (metrics), and OpenSearch (logs). Also scrapes infrastructure metrics directly.

## Receivers

| Receiver | Source |
|---|---|
| `otlp/grpc` (4317) | All services via OTLP gRPC |
| `otlp/http` (4318) | Services using HTTP exporter; browser traces via frontend-proxy |
| `httpcheck/frontend-proxy` | Probes frontend-proxy availability |
| `nginx` | Scrapes image-provider `/status` |
| `docker_stats` | Docker container metrics via `/var/run/docker.sock` |
| `postgresql` | PostgreSQL metrics at `POSTGRES_HOST:POSTGRES_PORT` |
| `redis` | Valkey metrics at `valkey-cart:6379` |
| `hostmetrics` | CPU, memory, disk, network from host filesystem |

## Exporters

- Jaeger: OTLP trace export
- Prometheus: metrics push/scrape
- OpenSearch: log export

## Key Source Files

- `src/otel-collector/otelcol-config.yml` — receivers, processors, exporters, pipelines
- `src/otel-collector/otelcol-config-extras.yml` — additional config (overrides, local customization)

## Risky Notes

1. The collector runs as root (`user: 0:0`) to access `/var/run/docker.sock` and `/hostfs`. This is required for `docker_stats` and `hostmetrics` receivers.
2. `GOMEMLIMIT=160MiB` is set. High telemetry volume (many services at once) can cause the collector to drop data if this limit is exceeded.
3. Two config files are merged at startup. The extras file (`otelcol-config-extras.yml`) can override any pipeline; workshop participants modifying it can silently break the full telemetry pipeline.
