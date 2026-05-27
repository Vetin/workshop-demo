# currency

## Identity

- **Language**: C++
- **Framework**: gRPC C++ with OpenTelemetry C++ SDK
- **Port**: 7001 (`CURRENCY_PORT`)
- **Dockerfile**: `src/currency/Dockerfile`
- **Main entry point**: `src/currency/src/` (C++ source; `CMakeLists.txt` at `src/currency/CMakeLists.txt`)

## Responsibility

Converts monetary amounts between currencies. Exposes `CurrencyService` gRPC methods: `GetSupportedCurrencies` and `Convert`.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| otel-collector | OTLP gRPC | Telemetry export |

No runtime service dependencies. Currency rates are embedded in the binary.

Environment variables: `CURRENCY_PORT`, `IPV6_ENABLED`, `VERSION`, `OTEL_EXPORTER_OTLP_ENDPOINT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry C++ SDK used manually. SDK version pinned via build arg `OPENTELEMETRY_CPP_VERSION` (currently 1.24.0 in `.env`).
- Common helpers in `src/currency/src/tracer_common.h`, `src/currency/src/meter_common.h`, `src/currency/src/logger_common.h`.
- **Exporter**: OTLP gRPC (env var `OTEL_EXPORTER_OTLP_ENDPOINT`).
- The C++ SDK is compiled from source inside the Docker build — making the build slow and sensitive to network access.

## gRPC Interface

Proto definition at `pb/demo.proto`:
```
service CurrencyService {
    rpc GetSupportedCurrencies(Empty) returns (GetSupportedCurrenciesResponse) {}
    rpc Convert(CurrencyConversionRequest) returns (Money) {}
}
```
Callers: checkout (`src/checkout/main.go`), frontend (`src/frontend/gateways/rpc/Currency.gateway.ts`).

Generated stubs: `src/currency/build/generated/proto/demo.grpc.pb.cc`, `src/currency/build/generated/proto/demo.pb.cc`.

## Key Source Files

- `src/currency/CMakeLists.txt` — build system
- `src/currency/src/` — C++ implementation files
- `src/currency/src/tracer_common.h` — OTel tracer setup
- `src/currency/src/meter_common.h` — OTel meter setup
- `src/currency/build/generated/proto/` — generated protobuf C++ stubs
- `src/currency/Dockerfile`

## Risky Notes

The C++ SDK is cloned and built from GitHub during `docker build`. A network failure or version removal on GitHub will break the build entirely. The `OPENTELEMETRY_CPP_VERSION` arg must stay in sync with any API changes in the C++ source files.
