# kafka

## Identity

- **Language**: Java / JVM
- **Framework**: Apache Kafka 3.9.1 (KRaft mode, no ZooKeeper)
- **Port**: 9092 (`KAFKA_PORT`)
- **Dockerfile**: `src/kafka/Dockerfile`
- **Main entry point**: N/A (standard Kafka broker, configured via env vars)

## Responsibility

Message broker for the `orders` topic. Receives messages from checkout (producer) and delivers to accounting and fraud-detection (consumers).

## Topic

| Topic | Producer | Consumers |
|---|---|---|
| `orders` | checkout | accounting, fraud-detection |

`KAFKA_AUTO_CREATE_TOPICS_ENABLE=true` — topics are created on first produce.

## Configuration

KRaft mode (no ZooKeeper):
- `KAFKA_PROCESS_ROLES=controller,broker`
- `KAFKA_NODE_ID=1`
- Single-node cluster (`KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1`).
- Advertised listener: `PLAINTEXT://${KAFKA_HOST}:9092`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Java agent injected via `KAFKA_OPTS=-javaagent:/tmp/opentelemetry-javaagent.jar -Dotel.jmx.target.system=kafka-broker` (set in `src/kafka/Dockerfile` line 25).
- JMX metrics for kafka-broker target exported to otel-collector.
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## Key Source Files

- `src/kafka/Dockerfile` — agent installation and configuration
- `.env` — `KAFKA_ADDR`, `KAFKA_HOST`, `KAFKA_PORT`

## Risky Notes

1. Single-node KRaft with replication factor 1 — no fault tolerance. Kafka restart loses in-flight messages.
2. The Java agent version (`OTEL_JAVA_AGENT_VERSION=2.23.0`) must match the agent used by ad and fraud-detection services for consistent telemetry schema.
3. Healthcheck uses `nc -z kafka 9092`. If the hostname `kafka` cannot resolve from within the container, all dependent services (checkout, accounting, fraud-detection) will fail to start.
