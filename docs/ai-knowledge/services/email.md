# email

## Identity

- **Language**: Ruby
- **Framework**: Sinatra
- **Port**: 6060 (`EMAIL_PORT`)
- **Dockerfile**: `src/email/Dockerfile`
- **Main entry point**: `src/email/email_server.rb`

## Responsibility

Sends order confirmation emails. Exposes a single HTTP endpoint `POST /send_order_confirmation`. Called by checkout over HTTP (not gRPC, despite `EmailService` being defined in the protobuf).

## Dependencies

| Dependency | Protocol | Purpose |
|---|---|---|
| flagd | gRPC (flagd Ruby provider) | Feature flag evaluation |
| otel-collector | OTLP HTTP | Telemetry export |

Environment variables: `EMAIL_PORT`, `FLAGD_HOST`, `FLAGD_PORT`.

## OTel Instrumentation

- **Approach**: OpenTelemetry Ruby SDK configured in `src/email/email_server.rb`.
- **Auto-instrumentation**: `opentelemetry-instrumentation-sinatra` used (`c.use "OpenTelemetry::Instrumentation::Sinatra"`).
- **Manual**: custom attributes added to auto-instrumented span (`app.order.id`).
- **Metrics**: custom counter `app.confirmation.counter` via `opentelemetry-metrics-sdk` (email_server.rb lines 38–41).
- **Logs**: `OpenTelemetry.logger_provider.logger(name: 'email')` (line 36).
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## HTTP Interface

`POST /send_order_confirmation` — JSON body with `order` object containing `order_id` and order items.

Note: checkout calls this via `EMAIL_ADDR=http://email:6060`. This is HTTP, not gRPC. The `EmailService` in `pb/demo.proto` is defined but the Ruby implementation does not serve a gRPC endpoint.

## Key Source Files

- `src/email/email_server.rb` — complete service implementation
- `src/email/Gemfile` — Ruby gem dependencies
- `src/email/views/` — email templates
- `src/email/Dockerfile`

## Risky Notes

The service uses HTTP instead of gRPC despite having a proto definition. Any caller must use the HTTP JSON format, not gRPC. The `SendOrderConfirmationRequest` proto message is not used at the wire level.
