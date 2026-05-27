# valkey-cart

## Identity

- **Language**: N/A
- **Framework**: Valkey 9.0.1 (Redis 7-compatible fork)
- **Port**: 6379 (`VALKEY_PORT`)
- **Dockerfile**: None — uses upstream `valkey/valkey:9.0.1-alpine3.23` image
- **Main entry point**: N/A

## Responsibility

In-memory key-value store exclusively used by the cart service for session cart data. Named `valkey-cart` to distinguish it from any other potential cache instances.

## Dependencies

None.

## OTel Instrumentation

- No agent on the Valkey container.
- Metrics scraped by otel-collector `redis` receiver at `valkey-cart:6379` (configured in `src/otel-collector/otelcol-config.yml` lines 48–51).

## Key Source Files

- N/A (upstream image, no local config)

## Risky Notes

Valkey is a Redis fork. The cart service uses `StackExchange.Redis` which is Redis-compatible. If Valkey introduces a protocol incompatibility in a future version, the `VALKEY_IMAGE` pin in `.env` must be updated carefully with the cart service's Redis client version.
