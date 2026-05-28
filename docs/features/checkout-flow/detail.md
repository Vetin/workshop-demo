# Feature: Checkout Flow — Detail

## Behavior

The checkout flow begins when a user clicks "Place Order" on the cart page. The
frontend BFF (`pages/api/checkout.ts`) forwards the form data to
`CheckoutService.PlaceOrder` via gRPC. The checkout service orchestrates all
downstream calls and returns an `OrderResult` to the BFF, which encodes it into
a URL query parameter and redirects the browser to the confirmation page.

### PlaceOrder sequence

1. `CartService.GetCart` — fetch cart items
2. `ProductCatalogService.GetProduct` per item — resolve product details
3. `CurrencyService.Convert` per item price + shipping — convert to user currency
4. `POST {shipping}/get-quote` — get shipping cost
5. If `gift_wrap=true`: `CurrencyService.Convert` of `$5 USD` gift wrap fee to
   user currency; `span.AddEvent("gift_wrap_fee_applied")` emitted
6. `PaymentService.Charge` — charge for total (items + shipping + gift wrap fee)
7. `POST {shipping}/ship-order` — generate tracking ID
8. `CartService.EmptyCart` — clear the cart
9. `POST {email}/send_order_confirmation` — send confirmation email
10. Kafka produce `orders` topic — `OrderResult` (protobuf)

### Gift wrap add-on

When the user checks "Add gift wrap (+$5.00)" on the cart page:

- `giftWrap: true` and `giftMessage: string` flow through `IFormData` →
  `CartDetail.onPlaceOrder` → `ApiGateway.placeOrder` → BFF POST body →
  gRPC `PlaceOrderRequest.gift_wrap` / `gift_message`
- Checkout service converts `$5 USD` to user currency, adds to order total,
  sets `app.order.gift_wrap=true` and `app.order.gift_wrap.amount` span attrs,
  emits `gift_wrap_fee_applied` span event
- `OrderResult` carries `gift_wrap: bool` and `gift_wrap_cost: Money`
- Confirmation page destructures these from the URL query param and renders a
  gift wrap fee row; `orderTotal` useMemo includes `gift_wrap_cost`
- `gift_message` is passed to `sendOrderConfirmation` as a separate argument;
  the HTTP POST body to the email service includes it as a top-level JSON field;
  it is **never** placed in any span attribute, event, or log field

---

## Contracts

### gRPC — `CheckoutService.PlaceOrder`

Defined in `pb/demo.proto`.

**`PlaceOrderRequest`** key fields:
```protobuf
string user_id = 1;
string user_currency = 2;
Address address = 3;
reserved 4;
string email = 5;
CreditCardInfo credit_card = 6;
bool gift_wrap = 7;      // NEW: gift wrap selection
string gift_message = 8; // NEW: optional personal message (PII — never in telemetry)
```

**`OrderResult`** key fields:
```protobuf
string order_id = 1;
string shipping_tracking_id = 2;
Money shipping_cost = 3;
Address shipping_address = 4;
repeated OrderItem items = 5;
bool gift_wrap = 6;       // NEW: mirrors request
Money gift_wrap_cost = 7; // NEW: converted fee in user currency
```

### HTTP — `POST /send_order_confirmation`

Served by the email service at `$EMAIL_ADDR/send_order_confirmation`.

Request body:
```json
{
  "email": "user@example.com",
  "order": {
    "order_id": "...",
    "shipping_tracking_id": "...",
    "shipping_cost": { "units": 8, "nanos": 990000000, "currency_code": "USD" },
    "gift_wrap": true,
    "gift_wrap_cost": { "units": 5, "nanos": 0, "currency_code": "USD" }
  },
  "gift_message": "Happy Birthday!"
}
```

Notes:
- `gift_message` is a **top-level** field (not nested in `order`) to keep PII
  out of the proto-serialized `OrderResult` and the Kafka payload
- `gift_wrap: false` is **omitted** from the JSON (proto3 `omitempty` on bool);
  the Ruby `OpenStruct` parser returns `nil` for absent keys
- `gift_message` is omitted entirely when `gift_wrap=false` or message is empty
- Called via `otelhttp.Post` (trace context propagation preserved)

---

## Telemetry

### Span attributes — checkout `PlaceOrder` span

| Attribute | Type | When set | Notes |
|---|---|---|---|
| `app.user.id` | string | always | Session UUID |
| `app.user.currency` | string | always | ISO 4217 code |
| `app.order.id` | string | always | UUID |
| `app.order.amount` | float64 | always | Total charged in user currency |
| `app.order.items.count` | int | always | Number of line items |
| `app.shipping.amount` | float64 | always | Shipping fee in user currency |
| `app.shipping.tracking.id` | string | always | |
| `app.payment.transaction.id` | string | always | |
| `app.payment.card_type` | string | always | |
| `app.loyalty.level` | string | always | |
| `app.cart.items.count` | int | always | |
| `app.order.gift_wrap` | bool | always | `true`/`false` on every order |
| `app.order.gift_wrap.amount` | float64 | gift_wrap=true only | Fee in user currency |

### Span events — checkout `PlaceOrder` span

| Event | When emitted |
|---|---|
| `"prepared"` | After price/shipping resolution |
| `"charged"` | After payment success |
| `"shipped"` | After ship-order success |
| `"gift_wrap_fee_applied"` | After gift wrap fee currency conversion (gift_wrap=true only) |

### Email service spans

| Span | Attributes |
|---|---|
| Sinatra auto-instrumentation (inbound) | `app.order.id` |
| `send_email` (manual) | `app.email.recipient` |

### Metrics

| Name | Type | Service | Labels |
|---|---|---|---|
| `app.payment.transactions` | counter | payment | `currency` |
| `app.confirmation.counter` | counter | email | (none) |

---

## Edge cases

| Case | Handling |
|---|---|
| Gift wrap checked, message empty | Valid; email shows no gift message section; empty string sent to checkout; checkout sends empty string to email; email ERB guard skips section |
| Gift wrap unchecked, message typed | `giftWrap=false` is authoritative; checkout sets `effectiveGiftMessage=""` before calling `sendOrderConfirmation` regardless of the `GiftMessage` field value |
| Currency conversion failure (gift wrap fee) | Same as item/shipping conversion failure — `PlaceOrder` returns an Internal gRPC error; order is not placed |
| Gift message exceeds 500 chars | Frontend `maxLength={500}` prevents submission; no backend enforcement (demo scope) |
| Gift message contains HTML/script | `CGI.escapeHTML(gift_message.to_s)` in `confirmation.erb` escapes all HTML entities; `<script>` becomes `&lt;script&gt;` |
| `gift_wrap: false` absent from JSON (proto3 omitempty) | Ruby `OpenStruct` returns `nil` for absent keys; ERB and handler treat `nil` as false |
| Load-generator synthetic traffic | Does not send `gift_wrap`; proto3 defaults (false/"") apply; `app.order.gift_wrap=false` is set on every PlaceOrder span |

---

## PII and sensitive data

`giftMessage` text is PII-equivalent (personal dedications, names). Enforcement:

| Rule | Location |
|---|---|
| Never set as span attribute | `src/checkout/main.go` (PlaceOrder), `src/email/email_server.rb` |
| Never written to structured log body or field | `src/checkout/main.go` (slog calls), email (OTLP logger) |
| Not included in `OrderResult` | Only `gift_wrap` bool and `gift_wrap_cost` Money flow into proto |
| Not in Kafka message | `OrderResult` carries no gift message |
| Flows only via HTTP POST to email service | `sendOrderConfirmation` HTTP payload |
| XSS-safe in email output | `CGI.escapeHTML(gift_message.to_s)` in ERB template |

---

## Tests

### Unit tests

| File | Tests |
|---|---|
| `src/checkout/checkout_test.go` | Gift wrap fee calculation, span attribute setting, `gift_message` not in span attributes, currency conversion path |
| `src/email/email_server_test.rb` | Gift message rendering, XSS escaping (`<script>` → `&lt;script&gt;`), nil guard, empty guard, PII non-leakage (8 runs, 25 assertions) |

### E2E tests (Cypress)

| File | Tests |
|---|---|
| `src/frontend/cypress/e2e/Checkout.cy.ts` | Gift wrap checkbox present; fee row appears/disappears on check/uncheck; textarea mounts/unmounts; POST body contains `giftWrap: true` and non-empty `giftMessage` |
| `src/frontend/cypress/e2e/Confirmation.cy.ts` | Gift wrap fee row visible and total `$ 15.00` on fixture order; fee row absent on standard order |

### Trace-based tests

| File | Status |
|---|---|
| `test/tracetesting/checkout/checkout_gift_wrap.yaml` | **Not yet created** — follow-up task FU-01 |

---

## Source paths

| File | Role |
|---|---|
| `pb/demo.proto` | Proto contract: `PlaceOrderRequest` fields 7–8, `OrderResult` fields 6–7 |
| `src/checkout/main.go` | `PlaceOrder` orchestration; gift wrap fee logic ~line 337; span attrs ~line 296, 359; event ~line 348; `sendOrderConfirmation` ~line 604 |
| `src/checkout/genproto/oteldemo/demo.pb.go` | Generated Go proto stubs |
| `src/email/email_server.rb` | HTTP handler, gift message extraction ~line 71, `send_email` span attrs |
| `src/email/views/confirmation.erb` | ERB template; gift message section with CGI.escapeHTML |
| `src/email/email_server_test.rb` | Ruby unit tests |
| `src/frontend/components/CheckoutForm/CheckoutForm.tsx` | Gift wrap checkbox, gift message textarea, `IFormData` |
| `src/frontend/components/CheckoutForm/GiftMessage.styled.ts` | `GiftWrapRow` + `GiftMessageTextarea` styled components |
| `src/frontend/components/CartItems/CartItems.tsx` | Gift wrap fee row in order summary |
| `src/frontend/components/Cart/CartDetail.tsx` | `giftWrap` state, `onGiftWrapChange` callback, placeOrder threading |
| `src/frontend/pages/api/checkout.ts` | BFF: forwards `giftWrap`/`giftMessage` to gRPC |
| `src/frontend/pages/cart/checkout/[orderId]/index.tsx` | Confirmation page: fee row, `orderTotal` useMemo |
| `src/frontend/utils/enums/CypressFields.ts` | `GiftWrapCheckbox`, `GiftMessageTextarea` enum values |
| `src/frontend/protos/demo.ts` | Generated TypeScript proto stubs |

---

## Known limitations

1. **Pre-order fee display in non-USD** — The cart page order summary shows the
   gift wrap fee as `$5.00 USD` regardless of the user's selected currency. The
   correct converted amount appears only on the confirmation page (from
   `OrderResult.gift_wrap_cost`). A `TODO` comment in `CartItems.tsx` marks
   this for a follow-on fix.

2. **Trace-based test gap** — `test/tracetesting/checkout/checkout_gift_wrap.yaml`
   has not been created. Span attribute and event correctness is verified by Go
   unit tests. See follow-up task FU-01.

3. **No gift wrap feature flag** — Gift wrap is always available. A rollout flag
   can be added in a follow-on change.

---

## Related changes

- `docs/features/checkout-flow/changes/gift-wrap-checkout/` — Delivery history
  for the initial gift wrap implementation (2026-05-27)
