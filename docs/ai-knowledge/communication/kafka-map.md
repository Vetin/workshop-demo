# Kafka Communication Map

---

## Broker

Single-node Kafka broker configured in `docker-compose.yml` (service `kafka`).

- Advertised listener: `PLAINTEXT://$KAFKA_HOST:9092`
- Health check: `nc -z kafka 9092`
- Image built from `$KAFKA_DOCKERFILE` with the OTel Java agent attached

---

## Topics

| Topic | Defined In | Message Format |
|-------|-----------|----------------|
| `orders` | `src/checkout/kafka/producer.go:13` | Protobuf-serialized `OrderResult` (from `pb/demo.proto`) |

Only one topic exists in this codebase. All Kafka traffic flows through `orders`.

---

## Producer

### checkout (Go)

| Property | Value | Source |
|----------|-------|--------|
| Topic | `orders` | `src/checkout/kafka/producer.go:13` |
| Library | `github.com/IBM/sarama` | `src/checkout/kafka/producer.go:9` |
| Producer type | `sarama.AsyncProducer` | `src/checkout/kafka/producer.go:31` |
| Message encoding | `proto.Marshal(OrderResult)` | `src/checkout/main.go:612` |
| Send location | `cs.sendToPostProcessor()` | `src/checkout/main.go:611-675` |
| Trigger | Called at end of `PlaceOrder` when `$KAFKA_ADDR` is set | `src/checkout/main.go:386-389` |
| Acks | `sarama.NoResponse` (no ack wait) | `src/checkout/kafka/producer.go:41` |
| Trace propagation | W3C TraceContext headers injected into Kafka message headers | `src/checkout/main.go:693-698` |

The producer fires only when `KAFKA_ADDR` environment variable is non-empty. If Kafka is absent, the order flow completes silently without the post-processing event.

---

## Consumers

### accounting (C# / .NET)

| Property | Value | Source |
|----------|-------|--------|
| Topic | `orders` | `src/accounting/Consumer.cs:29` |
| Consumer group | `accounting` | `src/accounting/Consumer.cs:143` |
| Library | `Confluent.Kafka` | `src/accounting/Consumer.cs:4` |
| Message decoding | `OrderResult.Parser.ParseFrom(message.Value)` | `src/accounting/Consumer.cs:90` |
| On message | Persists order to PostgreSQL via Entity Framework Core | `src/accounting/Consumer.cs:96-133` |
| Auto offset reset | `Earliest` | `src/accounting/Consumer.cs:146` |
| Auto commit | `true` | `src/accounting/Consumer.cs:147` |
| Broker address | `$KAFKA_ADDR` | `src/accounting/Consumer.cs:41` |

### fraud-detection (Kotlin / JVM)

| Property | Value | Source |
|----------|-------|--------|
| Topic | `orders` | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:7` |
| Consumer group | `fraud-detection` | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:8` |
| Library | `org.apache.kafka.clients.consumer.KafkaConsumer` | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:9` |
| Message decoding | `OrderResult.parseFrom(record.value())` | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:64` |
| On message | Logs order ID; checks `kafkaQueueProblems` feature flag (sleeps 1s per message when enabled) | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:60-66` |
| Broker address | `$KAFKA_ADDR` | `src/fraud-detection/src/main/kotlin/frauddetection/main.kt:42` |

---

## Flow Diagram

```
checkout (Go)
    |
    | proto.Marshal(OrderResult)
    | Topic: "orders"
    |
    +--> accounting (C#)
    |    Decodes OrderResult, writes to PostgreSQL
    |
    +--> fraud-detection (Kotlin)
         Decodes OrderResult, logs orderId
```

Both consumers are in separate consumer groups (`accounting`, `fraud-detection`), so both receive every message independently.

---

## Message Schema

The `OrderResult` message is defined in `pb/demo.proto`:

```
message OrderResult {
    string   order_id = 1;
    string   shipping_tracking_id = 2;
    Money    shipping_cost = 3;
    Address  shipping_address = 4;
    repeated OrderItem items = 5;
}
```

`OrderItem` contains a `CartItem` (product_id + quantity) and a `Money` cost field.

---

## Risky Patterns

1. **No-ack producer** — checkout uses `sarama.NoResponse` (`src/checkout/kafka/producer.go:41`), meaning messages can be silently lost if the broker is unavailable or overloaded. Failed sends are logged but do not fail the order RPC.

2. **Feature flag `kafkaQueueProblems` floods the topic** — when enabled, checkout sends `ffValue` additional duplicate messages for every order (`src/checkout/main.go:664-673`). fraud-detection sleeps 1 second per message under this flag, creating a consumer lag spiral.

3. **Single-topic fan-out** — both accounting and fraud-detection consume the same `orders` topic. Adding a third consumer requires no producer changes, but a schema change to `OrderResult` in `pb/demo.proto` requires redeploying all three services simultaneously.

4. **Protobuf deserialization without schema registry** — there is no schema registry or compatibility check. A proto field rename or removal in `pb/demo.proto` will cause consumers to silently drop or misinterpret fields after the producer redeploys.

5. **Kafka absence silently skips post-processing** — `src/checkout/main.go:386-389` only produces to Kafka when `$KAFKA_ADDR` is set. In environments without Kafka (e.g., minimal compose), orders complete without accounting or fraud-detection records.
