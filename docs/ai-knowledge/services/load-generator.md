# load-generator

## Identity

- **Language**: Python
- **Framework**: Locust + Playwright (browser traffic simulation)
- **Port**: 8089 (`LOCUST_WEB_PORT`)
- **Dockerfile**: `src/load-generator/Dockerfile`
- **Main entry point**: `src/load-generator/locustfile.py`

## Responsibility

Generates synthetic HTTP traffic against the frontend to simulate real user behavior. Also supports browser-level traffic via Playwright. Provides a Locust web UI accessible through frontend-proxy at `/loadgen/`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| frontend (via frontend-proxy) | HTTP | Traffic target (`LOCUST_HOST`) |
| flagd | gRPC (OFREP protocol) | Feature flag evaluation (`FLAGD_OFREP_PORT`) |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `LOCUST_WEB_PORT`, `LOCUST_USERS`, `LOCUST_HOST`, `LOCUST_HEADLESS`, `LOCUST_AUTOSTART`, `FLAGD_HOST`, `FLAGD_PORT`, `FLAGD_OFREP_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Python SDK configured manually in `src/load-generator/locustfile.py`.
- `TracerProvider` with `OTLPSpanExporter(insecure=True)`.
- `LoggerProvider` with `OTLPLogExporter`.
- `MeterProvider` with `OTLPMetricExporter`.
- Instrumentors: `Jinja2Instrumentor`, `RequestsInstrumentor`, `SystemMetricsInstrumentor`, `URLLib3Instrumentor`, `LoggingInstrumentor`.
- OpenFeature: `OFREPProvider` (uses OFREP HTTP port, not gRPC flagd port).

## Key Source Files

- `src/load-generator/locustfile.py` — all user tasks and OTel setup
- `src/load-generator/people.json` — synthetic user data
- `src/load-generator/Dockerfile`

## Risky Notes

Memory limit is 1500M (the highest of any service) due to Playwright browser instances. Reducing this will cause OOM crashes during browser traffic simulation.
