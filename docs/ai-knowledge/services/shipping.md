# shipping

## Identity

- **Language**: Rust
- **Framework**: Actix-web
- **Port**: 50050 (`SHIPPING_PORT`)
- **Dockerfile**: `src/shipping/Dockerfile`
- **Main entry point**: `src/shipping/src/main.rs`

## Responsibility

Provides shipping quotes and order shipment. Exposes two HTTP `POST` endpoints: `/get-quote` and `/ship-order`. Internally calls the quote service for price calculation.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| quote | HTTP | Get shipping cost quote (`QUOTE_ADDR=http://quote:8090`) |
| otel-collector | OTLP gRPC | Telemetry export |

Environment variables: `SHIPPING_PORT`, `QUOTE_ADDR`, `IPV6_ENABLED`.

## OTel Instrumentation

- **Approach**: `opentelemetry-instrumentation-actix-web` middleware applied in `src/shipping/src/main.rs`:
  - `RequestTracing::new()` — auto-creates spans for each HTTP request.
  - `RequestMetrics::default()` — auto-records HTTP duration metrics.
- **OTel init**: `src/shipping/src/telemetry_conf.rs` calls `init_otel()`.
- **Tracing crate**: `tracing` crate used for structured logging with `info!` macros.
- **Exporter**: OTLP gRPC.

## HTTP Interface

Although `ShippingService` is in the protobuf, shipping exposes HTTP (not gRPC):
- `POST /get-quote` — body: `GetQuoteRequest` JSON; response: `GetQuoteResponse` JSON
- `POST /ship-order` — body: `ShipOrderRequest` JSON; response: `ShipOrderResponse` JSON (tracking ID)

Callers: checkout calls `SHIPPING_ADDR=http://shipping:50050`, frontend calls via HTTP API gateway.

## Key Source Files

- `src/shipping/src/main.rs` — entry point, Actix-web server, middleware wiring
- `src/shipping/src/shipping_service.rs` — route handlers
- `src/shipping/src/telemetry_conf.rs` — OTel SDK initialization
- `src/shipping/Cargo.toml` — Rust dependencies
- `src/shipping/Dockerfile`

## Risky Notes

Shipping calls quote over HTTP at `QUOTE_ADDR`. If quote is down, `/get-quote` returns a 500. There is no circuit breaker or fallback. The Rust build uses cross-compilation for ARM64 targets (Dockerfile lines 13-19), requiring a specific cross-compilation toolchain.
