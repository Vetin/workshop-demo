# flagd

## Identity

- **Language**: N/A (pre-built binary from `ghcr.io/open-feature/flagd`)
- **Framework**: flagd (open-feature project)
- **Ports**: 8013 (`FLAGD_PORT`, gRPC), 8016 (`FLAGD_OFREP_PORT`, HTTP OFREP)
- **Dockerfile**: None — uses upstream image `${FLAGD_IMAGE}`
- **Main entry point**: `src/flagd/demo.flagd.json` (flag definitions, mounted at `/etc/flagd/demo.flagd.json`)

## Responsibility

Feature flag provider for all services. All services use the OpenFeature SDK to evaluate boolean, string, and numeric flags. Flags control error injection and demo scenario behaviors (e.g., `recommendationCacheFailure`, `kafkaQueueProblems`, `llmRateLimitError`).

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| otel-collector | gRPC | OTel metrics export (`FLAGD_METRICS_EXPORTER=otel`) |

No service-level dependencies — all other services depend on flagd.

Environment variables: `FLAGD_OTEL_COLLECTOR_URI=${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_GRPC}`, `FLAGD_METRICS_EXPORTER=otel`.

## OTel Instrumentation

- Built-in OTel metrics support via `FLAGD_METRICS_EXPORTER=otel`.
- Exports to otel-collector via gRPC (`FLAGD_OTEL_COLLECTOR_URI`).

## Flag File

`src/flagd/demo.flagd.json` is the live flag configuration. It is mounted as a volume in docker-compose (`./src/flagd:/etc/flagd`). The flagd-ui service also mounts the same path to allow editing flags through the UI.

## Protocols

- **gRPC** (port 8013): Used by all services that use the OpenFeature FlagdProvider (Go, Java, Kotlin, Python, C#, Ruby).
- **OFREP HTTP** (port 8016): Used by load-generator's `OFREPProvider`.

## Key Source Files

- `src/flagd/demo.flagd.json` — flag definitions (the only modifiable file)

## Risky Notes

The flagd flag file is shared between the `flagd` container and the `flagd-ui` container via a volume mount. Concurrent writes from flagd-ui while flagd is reading could cause transient parse errors.
