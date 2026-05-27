# Feature: Order Confirmation Email

## Behavior

After `CheckoutService.PlaceOrder` succeeds (card charged, order shipped), the checkout service calls the email service to send a confirmation to the buyer's address. The call is synchronous but non-fatal: a failure only produces a warning log; the order result is still returned to the frontend.

The email service renders an ERB template and dispatches via `Pony` (configured as a test mailer in the demo - no real SMTP). The `emailMemoryLeak` feature flag can inflate the email body and disable delivery clearing to simulate a memory leak.

## Services involved

| Service | Language | Role |
|---|---|---|
| checkout | Go | Calls the email service after shipping succeeds |
| email | Ruby / Sinatra | Renders confirmation template and sends email |

## Key API calls

| Step | Call |
|---|---|
| Send email | HTTP `POST {EMAIL_ADDR}/send_order_confirmation` with JSON `{ email, order }` |

The outgoing HTTP call from checkout uses `otelhttp.Post`, so it is automatically traced as a child span of the `PlaceOrder` span.

## Telemetry

- **Spans**: Sinatra auto-instrumentation span for `POST /send_order_confirmation`; manual `send_email` span inside the handler
- **Span attributes**: `app.order.id` (on the Sinatra span); `app.email.recipient` (on the `send_email` span)
- **Metrics**: `app.confirmation.counter` (counter, unit `"1"`) — one increment per request
- **Logs (OTLP)**: body `"Order confirmation email sent"`, attribute `app.email.recipient: <address>`

## Feature flags

| Flag | Effect |
|---|---|
| `emailMemoryLeak` | Multiplier applied to email body length (1x, 10x, 100x, 1000x, 10000x). When multiplier >= 1, sent emails accumulate in `Mail::TestMailer.deliveries` instead of being cleared. |

## Source paths

- `src/checkout/main.go` (function `sendOrderConfirmation`, call site in `PlaceOrder`)
- `src/email/email_server.rb`
- `src/email/views/confirmation.erb`
