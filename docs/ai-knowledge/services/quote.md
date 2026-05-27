# quote

## Identity

- **Language**: PHP 8.4
- **Framework**: Slim Framework (PSR-7/PSR-15)
- **Port**: 8090 (`QUOTE_PORT`)
- **Dockerfile**: `src/quote/Dockerfile`
- **Main entry point**: `src/quote/app/routes.php`

## Responsibility

Calculates shipping cost quotes based on item count. Called by shipping service over HTTP. No database dependency — computation is purely in-memory.

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| otel-collector | OTLP HTTP | Telemetry export |

No runtime service dependencies. Called by: shipping (`QUOTE_ADDR=http://quote:8090`).

Environment variables: `QUOTE_PORT`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `IPV6_ENABLED`.

## OTel Instrumentation

- **Approach**: OpenTelemetry PHP SDK with autoload (`OTEL_PHP_AUTOLOAD_ENABLED=true`).
- **Internal metrics**: `OTEL_PHP_INTERNAL_METRICS_ENABLED=true`.
- **Manual**: `Globals::tracerProvider()->getTracer('manual-instrumentation')` used in `routes.php` to create a child span `calculate-quote`.
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## HTTP Interface

Called by shipping at `QUOTE_ADDR=http://quote:8090`. The Slim route is in `src/quote/app/routes.php`.

## Key Source Files

- `src/quote/app/routes.php` — HTTP route handlers with manual OTel spans
- `src/quote/src/` — Slim app bootstrap
- `src/quote/composer.json` — PHP dependencies
- `src/quote/public/` — web root / front controller
- `src/quote/Dockerfile`

## Risky Notes

Quote is the only PHP service in the system. The `opentelemetry` PHP extension is installed via `install-php-extensions opentelemetry` in the Dockerfile. Version drift between the PHP extension and the SDK package in `composer.json` can cause silent instrumentation failures.
