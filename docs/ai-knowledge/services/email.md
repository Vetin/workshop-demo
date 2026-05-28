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
- **Manual span attributes**:
  - `app.order.id` — set on the auto-instrumented Sinatra span (`email_server.rb:50`)
  - `app.email.recipient` — set on the manual `send_email` child span (`email_server.rb:88`)
- **Metrics**: custom counter `app.confirmation.counter` via `opentelemetry-metrics-sdk` (email_server.rb lines 38–41).
- **Logs**: `OpenTelemetry.logger_provider.logger(name: 'email')` (line 36). Log body `'Order confirmation email sent'` with attribute `app.email.recipient`.
- **Exporter**: OTLP HTTP (`http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_HTTP}`).

## HTTP Interface

`POST /send_order_confirmation` — JSON body fields:

| Field | Type | Notes |
|---|---|---|
| `email` | string | Recipient address |
| `order` | object | Contains `order_id`, `shipping_tracking_id`, `shipping_cost`, `shipping_address`, `items` |
| `gift_message` | string | Optional. Passed by checkout only when `gift_wrap=true`. Rendered in confirmation email template but never recorded in any span, log field, or metric label (PII constraint). |

Note: checkout calls this via `EMAIL_ADDR=http://email:6060`. This is HTTP, not gRPC. The `EmailService` in `pb/demo.proto` is defined but the Ruby implementation does not serve a gRPC endpoint.

The confirmation email template (`src/email/views/confirmation.erb`) conditionally renders a "Gift Message" section when `gift_message` is present and non-empty, HTML-escaped via `CGI.escapeHTML`.

## Key Source Files

- `src/email/email_server.rb` — complete service implementation
- `src/email/email_server_test.rb` — unit tests covering gift message rendering, XSS escaping, nil/empty guards, PII non-leakage
- `src/email/Gemfile` — Ruby gem dependencies
- `src/email/views/` — email templates
- `src/email/Dockerfile`

## Risky Notes

The service uses HTTP instead of gRPC despite having a proto definition. Any caller must use the HTTP JSON format, not gRPC. The `SendOrderConfirmationRequest` proto message is not used at the wire level.
