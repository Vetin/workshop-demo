# ad

## Identity

- **Language**: Java 21
- **Framework**: gRPC Java (eclipse-temurin JRE base image)
- **Port**: 9555 (`AD_PORT`)
- **Dockerfile**: `src/ad/Dockerfile`
- **Main entry point**: `src/ad/src/main/java/oteldemo/AdService.java`

## Responsibility

Serves contextual advertisement text to the frontend based on product category context keys. Exposes `AdService.GetAds` gRPC method.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| flagd | gRPC (FlagdProvider) | Feature flag evaluation (GC trigger, CPU load scenarios) |
| otel-collector | OTLP HTTP | Telemetry export |

Environment variables: `AD_PORT`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Java agent injected via `JAVA_TOOL_OPTIONS=-javaagent:/usr/src/app/opentelemetry-javaagent.jar` (set in `src/ad/Dockerfile` line 32).
- **Manual instrumentation**: Uses `@WithSpan`, `@SpanAttribute` annotations from `opentelemetry-instrumentation-annotations`; manual `Tracer` and `Meter` usage visible in `AdService.java` lines 22-24.
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).
- **Logs**: `OTEL_LOGS_EXPORTER=otlp`.
- **Metrics temporality**: `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service AdService {
    rpc GetAds(AdRequest) returns (AdResponse) {}
}
```
Callers: frontend (`src/frontend/gateways/rpc/Ad.gateway.ts`).

## Build

Gradle build in `src/ad/build.gradle`. Proto sources compiled from `./proto/` directory inside the build container.

## Key Source Files

- `src/ad/src/main/java/oteldemo/AdService.java` — gRPC service implementation
- `src/ad/build.gradle` — build configuration with protobuf plugin
- `src/ad/Dockerfile`

## Risky Notes

The Java agent version is pinned via build arg `OTEL_JAVA_AGENT_VERSION` (currently 2.23.0 in `.env`). Upgrading the agent while keeping old manual annotation imports can cause duplicate span creation.
