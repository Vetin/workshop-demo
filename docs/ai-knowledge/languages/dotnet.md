# .NET Language Knowledge

Services:
- `src/accounting/` — C#/.NET 10, ASP.NET Core, Kafka consumer
- `src/cart/` — C#/.NET 10, ASP.NET Core, gRPC, Valkey (StackExchange.Redis)

## Version and Toolchain

- .NET 10 / ASP.NET Core
- C# language features up to C# 13

## Commands

| Task | Command | Working Directory |
|---|---|---|
| Build | `dotnet build` | `src/accounting/` or `src/cart/` |
| Test | `dotnet test` | service directory |
| Format | `dotnet format` | service directory |
| Restore | `dotnet restore` | service directory |

## OpenTelemetry Instrumentation — Per Service

### accounting (`src/accounting/`)

Uses .NET auto-instrumentation via the official `instrument.sh` script:

- **`instrument.sh` MUST remain the container entrypoint.** Removing it silently
  disables all OTel instrumentation for this service.
- OTLP HTTP exporter configured via `OTEL_EXPORTER_OTLP_ENDPOINT`.
- No manual `ActivitySource` in accounting — instrumentation is fully automatic.

### cart (`src/cart/`)

Uses manual `ActivitySource` alongside `OpenTelemetry.Extensions.Hosting`:

```csharp
private static readonly ActivitySource ActivitySource =
    new ActivitySource("cart");

using var activity = ActivitySource.StartActivity("AddItem");
activity?.SetTag("cart.item.product_id", productId);
```

Registered instrumentations in `Program.cs`:

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(b => b
        .AddAspNetCoreInstrumentation()
        .AddGrpcClientInstrumentation()
        .AddRedisInstrumentation()   // StackExchange.Redis
        .AddOtlpExporter());
```

OTLP gRPC exporter.

## Key C# Idioms

- `async`/`await` throughout — no blocking `.Result` or `.Wait()` on tasks.
- `ILogger<T>` injected via DI — never use `Console.Write` for diagnostics.
- `ActivitySource` declared as `private static readonly` at class level — not
  per-request.
- Never store `Activity.Current` in a field or variable that outlives the
  current stack frame — it is thread-local and becomes stale.
- Use `CancellationToken` parameters on every async method and propagate them
  to downstream calls.

## Common Failure Modes

| Symptom | Root Cause |
|---|---|
| Accounting service emits no traces | `instrument.sh` removed from or overridden in Dockerfile `CMD`/`ENTRYPOINT` |
| Hardcoded OTLP endpoint | `OTEL_EXPORTER_OTLP_ENDPOINT` env var replaced with literal string in code |
| `Activity.Current` is null or wrong | Stored in a field during async operation; retrieve it fresh from `Activity.Current` each call |
| Redis spans missing | `AddRedisInstrumentation()` removed from DI registration |
| gRPC client spans missing | `AddGrpcClientInstrumentation()` removed |

## Implementer Rules

1. Never modify the `instrument.sh` entrypoint in `src/accounting/Dockerfile`.
2. Never hardcode `OTEL_EXPORTER_OTLP_ENDPOINT` — always read from env.
3. In cart, preserve `AddAspNetCoreInstrumentation()`, `AddGrpcClientInstrumentation()`,
   and `AddRedisInstrumentation()` in the DI setup.
4. Do not store `Activity.Current` in instance fields.
5. Always propagate `CancellationToken` to downstream async calls.

## Reviewer Checks

- `async void` methods (should be `async Task` except for event handlers).
- Missing `CancellationToken` parameter on new async methods.
- `ActivityKind` set incorrectly (client calls should be `ActivityKind.Client`,
  incoming should be `ActivityKind.Server`).
- `Activity.Current` captured in a field.
- `instrument.sh` removed from accounting Dockerfile.
- `.Result` or `.Wait()` calls on `Task` objects (deadlock risk).
