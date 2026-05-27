# Order Confirmation Email - Overview

After a successful checkout, the checkout service sends an order confirmation email to the address provided at checkout. The email is sent synchronously within the `PlaceOrder` gRPC call. A failure to send is non-fatal: it is logged as a warning and the order result is still returned to the frontend.

## Services involved

- **checkout** (Go) - calls the email service after the card is charged and the order is shipped
- **email** (Ruby / Sinatra HTTP) - renders the confirmation template and dispatches the email via Pony

## User journey (summary)

1. Checkout service finishes charging the card and shipping the order.
2. Checkout service POSTs to `{EMAIL_ADDR}/send_order_confirmation` with `{ email, order }`.
3. Email service renders an ERB template (`confirmation.erb`) and sends via `Pony.mail`.
4. Email service returns 200; checkout logs `"order confirmation email sent to <email>"`.
5. If the POST fails or returns non-200, checkout logs a warning and continues.

## Feature flags

| Flag | Effect |
|---|---|
| `emailMemoryLeak` | Multiplies the email body size by the flag value (1x, 10x, 100x, 1000x, 10000x). When value >= 1, sent emails are not cleared from `Mail::TestMailer.deliveries`, causing memory accumulation. |
