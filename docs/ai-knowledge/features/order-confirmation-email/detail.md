# Order Confirmation Email - Detail

## Checkout side

File: `src/checkout/main.go`, function `sendOrderConfirmation`

Called from `PlaceOrder` after `shipOrder` succeeds:

```go
if err := cs.sendOrderConfirmation(ctx, req.Email, orderResult); err != nil {
    logger.Warn(fmt.Sprintf("failed to send order confirmation to %q: %+v", req.Email, err))
} else {
    logger.Info(fmt.Sprintf("order confirmation email sent to %q", req.Email))
}
```

The function marshals `{email, order}` to JSON and POSTs to `{EMAIL_ADDR}/send_order_confirmation` using `otelhttp.Post`. This means the outbound HTTP call is automatically traced as a child span of the `PlaceOrder` span. Non-200 responses are treated as errors and surfaced as the returned error.

## Email service

File: `src/email/email_server.rb`

Language: Ruby. Sinatra web server on `EMAIL_PORT`. Auto-instrumented via `OpenTelemetry::Instrumentation::Sinatra`.

### POST /send_order_confirmation

Handler:
1. Parses the JSON body into an `OpenStruct`.
2. Gets the current auto-instrumented Sinatra span and sets `app.order.id` on it.
3. Increments counter `app.confirmation.counter` (unit: `"1"`).
4. Calls `send_email(data)`.

### send_email

Creates a manual child span `send_email` using `tracer.in_span("send_email")`.

Inside the span:
1. Checks `emailMemoryLeak` feature flag (float via OpenFeature). Default 0.
2. Renders the ERB template: `erb(:confirmation, locals: { order: data.order })`.
3. Computes whitespace padding: `max(0, body_length * (multiplier - 1))` characters of spaces appended to the email body.
4. Sends email via `Pony.mail(to:, from: "noreply@example.com", subject: "Your confirmation email", body:, via: :test)`.
5. If `memory_leak_multiplier < 1`, clears `Mail::TestMailer.deliveries`. Otherwise leaves them, causing accumulation.
6. Sets span attribute `app.email.recipient` (the recipient email address).
7. Emits an OTLP log record with body `"Order confirmation email sent"` and attribute `app.email.recipient`.

Template: `src/email/views/confirmation.erb`

## Telemetry

Spans:
- Sinatra auto-instrumentation span for `POST /send_order_confirmation`: attribute `app.order.id`
- Manual `send_email` span: attribute `app.email.recipient`

Metrics:
- `app.confirmation.counter` (counter, unit: `"1"`) - one increment per call

Logs (OTLP):
- Body: `"Order confirmation email sent"`, attribute: `app.email.recipient: <address>`
