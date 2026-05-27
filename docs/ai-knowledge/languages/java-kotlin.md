# Java / Kotlin Language Knowledge

Services:
- `src/ad/` — Java 21, Spring Boot, gRPC
- `src/fraud-detection/` — Kotlin / JDK 21, Spring Boot, Kafka consumer
- `src/kafka/` — Kafka KRaft broker config (Java-based, config only)

## Version and Toolchain

- JDK 21+
- Gradle build system (`./gradlew`)
- Kotlin 1.9+ for fraud-detection

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Build | `./gradlew build` | `src/ad/` or `src/fraud-detection/` |
| Test | `./gradlew test` | service directory |
| Lint | `./gradlew checkstyleMain` (if configured) | service directory |
| Clean | `./gradlew clean` | service directory |

## OpenTelemetry Instrumentation — Per Service

### ad (`src/ad/`)

Uses the OpenTelemetry Java agent (zero-code instrumentation):

```
JAVA_TOOL_OPTIONS=-javaagent:/usr/share/java/opentelemetry-javaagent.jar
```

- Agent jar path must match the path in the Dockerfile `COPY` instruction.
- OTLP HTTP exporter configured via `OTEL_EXPORTER_OTLP_ENDPOINT`.
- No manual span creation in ad service — all instrumentation is automatic via
  Spring Boot and gRPC auto-instrumentation.

### fraud-detection (`src/fraud-detection/`)

Also uses the Java agent via `JAVA_TOOL_OPTIONS`. Additionally:

- Kafka experimental span attributes enabled via:
  ```
  OTEL_INSTRUMENTATION_KAFKA_EXPERIMENTAL_SPAN_ATTRIBUTES=true
  ```
- This enables `messaging.kafka.*` attributes on consumer spans — do not remove
  this env var.

### kafka (`src/kafka/`)

Kafka broker instrumented for JMX metrics via:

```
KAFKA_OPTS=-javaagent:/usr/share/java/opentelemetry-javaagent.jar
```

JMX scraper configuration exists alongside the broker config. The broker itself
is config-only; do not add application code here.

## Generated Code

No gRPC generated stubs in ad or fraud-detection. Both services load proto
definitions at runtime via the Java agent's gRPC instrumentation.

## Key Java Idioms

- Always handle checked exceptions — do not swallow them with empty `catch` blocks.
- Use try-with-resources for any `Closeable` resource:
  ```java
  try (var stream = Files.newInputStream(path)) {
      // ...
  }
  ```
- Prefer `Optional<T>` over returning `null` from methods.
- Spring beans are singleton by default — avoid mutable instance state.

## Key Kotlin Idioms

- Use `data class` for DTOs (immutable value containers).
- Leverage null safety: prefer `?.` and `?:` over `!!` — the `!!` operator is a
  code smell and will crash on null.
- Coroutines (`suspend` functions) may be used; always propagate coroutine context
  for OTel trace propagation if coroutines are introduced.
- Use `when` expression instead of `if-else if` chains.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| Agent not active; no traces emitted | `JAVA_TOOL_OPTIONS` not set in Dockerfile or K8s manifest |
| Agent jar `ClassNotFoundException` | Agent jar path in `JAVA_TOOL_OPTIONS` does not match `COPY` path in Dockerfile |
| Kafka spans missing messaging attributes | `OTEL_INSTRUMENTATION_KAFKA_EXPERIMENTAL_SPAN_ATTRIBUTES` removed |
| Consumer group offset reset causing duplicate processing | Consumer group ID changed or `auto.offset.reset=earliest` left on in production |
| `NullPointerException` in Kotlin | `!!` operator used; replace with safe call or explicit null check |

## Implementer Rules

1. Never change the agent jar path in `JAVA_TOOL_OPTIONS` without updating the
   `COPY` line in the same Dockerfile.
2. Do not remove `OTEL_INSTRUMENTATION_KAFKA_EXPERIMENTAL_SPAN_ATTRIBUTES` from
   fraud-detection.
3. Avoid adding manual `Span` creation in ad or fraud-detection — the Java agent
   handles it; manual spans can cause double-instrumentation.
4. In Kotlin, ban `!!` on nullable types derived from external sources (Kafka
   message fields, HTTP headers).

## Reviewer Checks

- Agent jar `COPY` and `JAVA_TOOL_OPTIONS` path mismatch in Dockerfile.
- `JAVA_TOOL_OPTIONS` absent from K8s `env:` section (common oversight when
  updating Helm values).
- `!!` (Kotlin not-null assertion) on values that could realistically be null.
- Empty `catch (Exception e) {}` blocks hiding errors.
- Resources not closed in try-with-resources (Java).
- Spring `@Autowired` field injection on non-Spring-managed class.
