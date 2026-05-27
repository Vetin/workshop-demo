# fraud-detection

## Identity

- **Language**: Kotlin / JVM
- **Framework**: Apache Kafka consumer (no HTTP or gRPC server)
- **Port**: None exposed
- **Dockerfile**: `src/fraud-detection/Dockerfile`
- **Main entry point**: `src/fraud-detection/src/main/kotlin/frauddetection/main.kt`

## Responsibility

Consumes the `orders` Kafka topic and evaluates transactions for fraud signals. Pure background consumer — no inbound connections.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| kafka | Kafka consumer (PLAINTEXT) | Reads `orders` topic |
| flagd | gRPC (FlagdProvider Java) | Feature flag evaluation (`kafkaQueueProblems`) |
| otel-collector | OTLP HTTP | Telemetry export |

Environment variables: `KAFKA_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Java agent via `JAVA_TOOL_OPTIONS=-javaagent:...` set in `src/fraud-detection/Dockerfile`.
- **Kafka-specific**: `OTEL_INSTRUMENTATION_KAFKA_EXPERIMENTAL_SPAN_ATTRIBUTES=true` and `OTEL_INSTRUMENTATION_MESSAGING_EXPERIMENTAL_RECEIVE_TELEMETRY_ENABLED=true` enable experimental Kafka span attributes and receive-side telemetry.
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## Kafka Consumer Details

- Group ID: `fraud-detection` (`main.kt` line 3: `const val groupID = "fraud-detection"`)
- Topic: `orders` (`main.kt` line 2: `const val topic = "orders"`)
- Message value: protobuf-encoded `OrderResult` (deserialized from `ByteArray`)
- Feature flag `kafkaQueueProblems` affects consumer behavior (introduces artificial delays)

## Key Source Files

- `src/fraud-detection/src/main/kotlin/frauddetection/main.kt` — full consumer implementation
- `src/fraud-detection/build.gradle.kts` — Gradle Kotlin DSL build
- `src/fraud-detection/Dockerfile`

## Risky Notes

Like accounting, protobuf deserialization of `OrderResult` is done at runtime with no compile-time contract check against the `pb/demo.proto` source. Schema drift in checkout's Kafka message will silently break fraud detection.
