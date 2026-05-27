# accounting

## Identity

- **Language**: C# / .NET 10
- **Framework**: ASP.NET Core (hosted service pattern, no HTTP listener)
- **Port**: None exposed externally
- **Dockerfile**: `src/accounting/Dockerfile`
- **Main entry point**: `src/accounting/Program.cs`

## Responsibility

Consumes `orders` Kafka topic and persists completed orders into PostgreSQL. No inbound HTTP or gRPC — it is a pure background consumer.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| kafka | Kafka consumer (PLAINTEXT) | Reads `orders` topic |
| postgresql | PostgreSQL (TCP) via Entity Framework Core + Npgsql | Persists order, order items, shipping records |

Environment variables: `KAFKA_ADDR`, `DB_CONNECTION_STRING`.

## OTel Instrumentation

- **Approach**: OpenTelemetry .NET auto-instrumentation. The Dockerfile runs `./instrument.sh dotnet Accounting.dll` at line 36 of `src/accounting/Dockerfile`.
- **Additional**: `OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES=Accounting.Consumer` registers the manual `ActivitySource` declared in `src/accounting/Consumer.cs` (line 35: `new ActivitySource("Accounting.Consumer")`).
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).
- **Entity Framework tracing disabled**: `OTEL_DOTNET_AUTO_TRACES_ENTITYFRAMEWORKCORE_INSTRUMENTATION_ENABLED=false`.

## Kafka Consumer Details

- Group ID: `accounting` (`src/accounting/Consumer.cs` line 144)
- Topic: `orders`
- Message value: protobuf-encoded `OrderResult` (`src/accounting/Consumer.cs` line 91: `OrderResult.Parser.ParseFrom(message.Value)`)
- Auto-offset reset: Earliest; auto-commit enabled

## Key Source Files

- `src/accounting/Program.cs` — entry point, DI setup
- `src/accounting/Consumer.cs` — Kafka consumer loop + PostgreSQL writes
- `src/accounting/Entities.cs` — EF Core entity types
- `src/accounting/Helpers.cs` — env var utilities
- `src/accounting/Dockerfile`

## Risky Notes

Protobuf deserialization of `OrderResult` is done without schema validation. If checkout changes the `OrderResult` message structure in `pb/demo.proto` without regenerating `src/accounting/`, parsing will silently fail or produce corrupt data. The only signal is a logged `Order parsing failed:` exception in `Consumer.cs` line 136.
