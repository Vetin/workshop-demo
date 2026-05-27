# cart

## Identity

- **Language**: C# / .NET 10
- **Framework**: ASP.NET Core with gRPC
- **Port**: 7070 (`CART_PORT`)
- **Dockerfile**: `src/cart/src/Dockerfile`
- **Main entry point**: `src/cart/src/Program.cs`

## Responsibility

Stores and retrieves per-user shopping carts backed by Valkey (Redis-compatible). Exposes `CartService` gRPC methods: `AddItem`, `GetCart`, `EmptyCart`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| valkey-cart | Redis protocol (StackExchange.Redis) | Cart persistence |
| flagd | gRPC (FlagdProvider) | Feature flags |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `CART_PORT`, `VALKEY_ADDR`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry .NET SDK configured manually in `src/cart/src/Program.cs`.
- **Libraries used**: `OpenTelemetry.Instrumentation.StackExchangeRedis` for auto-instrumenting Valkey calls (line 21 of Program.cs).
- **Logs**: `.AddOpenTelemetry(options => options.AddOtlpExporter())` (Program.cs line 38–40).
- **Exporter**: OTLP (endpoint from `OTEL_EXPORTER_OTLP_ENDPOINT` env var, defaults to gRPC port 4317).
- **OpenFeature hooks**: `MetricsHook` and `TraceEnricherHook` added (Program.cs lines 51-54).

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service CartService {
    rpc AddItem(AddItemRequest) returns (Empty) {}
    rpc GetCart(GetCartRequest) returns (Cart) {}
    rpc EmptyCart(EmptyCartRequest) returns (Empty) {}
}
```
Callers: checkout (`src/checkout/main.go` line 146 `cartSvcClient`), frontend (`src/frontend/gateways/rpc/Cart.gateway.ts`).

## Key Source Files

- `src/cart/src/Program.cs` — entry point, gRPC + OTel setup
- `src/cart/src/cartstore/ValkeyCartStore.cs` — Redis store implementation
- `src/cart/src/services/CartService.cs` — gRPC service handlers
- `src/cart/src/Dockerfile`

## Risky Notes

The Dockerfile is at `src/cart/src/Dockerfile`, not `src/cart/Dockerfile`. The `.env` variable `CART_DOCKERFILE=./src/cart/src/Dockerfile` correctly accounts for this, but it is an unusual path that can cause confusion.
