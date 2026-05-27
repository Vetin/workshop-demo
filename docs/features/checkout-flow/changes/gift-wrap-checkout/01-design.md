# Change Design

## Metadata

- feature area: checkout-flow
- change slug: gift-wrap-checkout
- request type: feature
- status: draft
- created by: sdd-orchestrator
- reviewed by:
- approved by:

---

## User request

> Add gift wrap and optional gift message to checkout. The user can select gift wrap during checkout, see the gift wrap fee in the order summary, add an optional gift message, and see the gift message in the confirmation email. Gift wrap selection may be recorded in telemetry, but the gift message text must never be recorded in telemetry.

---

## Business goal

Allow shoppers to add gift wrapping to their order during checkout. The feature surfaces a gift wrap fee transparently in the order summary and delivers the shopper's personal message to the recipient via the confirmation email, while ensuring the message text never appears in observability signals.

---

## Existing feature docs consulted

- `docs/features/checkout-flow/overview.md` — checkout orchestration, services, telemetry, source paths
- `docs/features/order-confirmation-email.md` — email service HTTP contract, ERB template, telemetry

---

## Existing system knowledge consulted

- `docs/ai-knowledge/architecture/overview.md` — service inventory, communication patterns
- `docs/ai-knowledge/communication/overview.md` — gRPC/HTTP/Kafka topology, risky change areas
- `docs/ai-knowledge/observability/overview.md` — sensitive data rules, span attribute conventions
- `docs/ai-knowledge/frontend/overview.md` — Pages Router, styled-components, React Query, OpenFeature

---

## User/system flow

```
1. User fills out checkout form (address, email, credit card)
2. NEW: "Add gift wrap (+$5.00)" checkbox is shown in the order summary panel
3. User checks the gift wrap checkbox
   → Gift wrap fee line item appears in the order summary (converted to user currency)
   → Optional "Gift message" textarea appears below the checkbox
4. User optionally types a gift message (max 500 chars, frontend validation only)
5. User clicks "Place Order"
6. Frontend BFF (pages/api/checkout.ts):
   - Reads gift_wrap (bool) and gift_message (string) from request body
   - Passes them to CheckoutService.PlaceOrder via gRPC
7. Checkout service (PlaceOrder):
   a. Reads gift_wrap and gift_message from PlaceOrderRequest
   b. If gift_wrap=true, converts $5.00 USD to user currency via CurrencyService.Convert
   c. Adds gift wrap cost to order total
   d. Constructs OrderResult with gift_wrap=true/false and gift_wrap_cost
   e. Charges card for updated total (includes gift wrap fee)
   f. Sets span attribute app.order.gift_wrap = true/false
   g. Does NOT set any span attribute or log field for gift_message text
   h. Calls sendOrderConfirmation with gift_message in HTTP payload
   i. Publishes OrderResult to Kafka (gift_wrap fields included for downstream audit)
8. Email service (send_order_confirmation):
   - Receives JSON: { email, order, gift_message }
   - Renders confirmation.erb with gift message section if gift_message is non-empty
   - Does NOT set any span attribute for gift_message text
9. User sees order confirmation page:
   - Shows gift wrap fee as a line item
   - Frontend knows gift_wrap=true from OrderResult; renders fee from gift_wrap_cost
```

---

## Services touched

| Service | Language | What changes |
|---|---|---|
| **frontend** | TypeScript/Next.js | Checkout form: gift wrap checkbox + gift message textarea. Order summary: gift wrap fee line item. Confirmation page: gift wrap fee from OrderResult. BFF route: forwards gift_wrap + gift_message to gRPC. |
| **checkout** | Go | PlaceOrder: read gift_wrap/gift_message; apply fee via CurrencyService; add to total; set `app.order.gift_wrap` span attribute; extend sendOrderConfirmation call; populate OrderResult gift fields. |
| **email** | Ruby/Sinatra | HTTP handler: extract gift_message from JSON payload. ERB template: conditional gift message section. |
| **pb/demo.proto** | protobuf | `PlaceOrderRequest`: add `gift_wrap` (bool, field 7) and `gift_message` (string, field 8). `OrderResult`: add `gift_wrap` (bool, field 6) and `gift_wrap_cost` (Money, field 7). |
| **Generated code** | Go, TypeScript | Regenerate after proto change: `src/checkout/genproto/`, `src/frontend/protos/demo.ts`. Other generated stubs (Python, C++, Node.js runtime) also re-generated but no logic changes in those services. |

---

## Contracts touched

### 1. `pb/demo.proto` — gRPC contract (HIGH RISK — affects all language stubs)

**`PlaceOrderRequest`** — add two fields:
```protobuf
message PlaceOrderRequest {
    string user_id = 1;
    string user_currency = 2;
    Address address = 3;
    string email = 5;
    CreditCardInfo credit_card = 6;
    // NEW:
    bool gift_wrap = 7;
    string gift_message = 8;
}
```

**`OrderResult`** — add two fields:
```protobuf
message OrderResult {
    string   order_id = 1;
    string   shipping_tracking_id = 2;
    Money    shipping_cost = 3;
    Address  shipping_address = 4;
    repeated OrderItem items = 5;
    // NEW:
    bool  gift_wrap = 6;
    Money gift_wrap_cost = 7;
}
```

Both changes are **backward compatible** (proto3 field addition with new field numbers). Existing consumers that do not read the new fields continue to work without modification.

**Generated code that must be regenerated:**
- Go: `src/checkout/genproto/oteldemo/` (checkout uses PlaceOrderRequest + OrderResult)
- TypeScript: `src/frontend/protos/demo.ts` (frontend calls PlaceOrder, reads OrderResult)
- Python: `src/recommendation/demo_pb2*.py`, `src/product-reviews/demo_pb2*.py` (regenerate; no logic change needed)
- C++: `src/currency/build/generated/proto/` (regenerate; no logic change needed)
- Node.js runtime (payment): loaded at runtime; no explicit code change needed

**C# and Kotlin consumers (Kafka):** accounting and fraud-detection deserialize `OrderResult` via Kafka. Proto3 new optional fields default to zero/false. No code changes required in those services unless they choose to act on gift_wrap.

### 2. HTTP `POST {email}/send_order_confirmation` — JSON body extension

Current payload:
```json
{ "email": "...", "order": { ... } }
```

New payload:
```json
{ "email": "...", "order": { ..., "gift_wrap": true, "gift_wrap_cost": {...} }, "gift_message": "..." }
```

The `gift_message` is a top-level field (not nested in `order`) to avoid coupling it to the `OrderResult` proto struct. This is an **additive change** — the existing email handler parses with `OpenStruct` and will simply have a new `gift_message` field available.

### 3. Frontend BFF `POST /api/checkout` — JSON body extension

The browser POST body already forwards the full checkout form. Two new optional fields:
- `gift_wrap: boolean` (default: `false`)
- `gift_message: string` (default: `""`)

---

## Frontend/UI-kit/Figma impact

### New UI elements (all in checkout page area)

| Element | Component | Styling approach |
|---|---|---|
| Gift wrap checkbox + label | New section in `CartDetail.tsx` or a sibling `GiftOptions.tsx` | styled-components, Theme tokens |
| Gift wrap fee line item | Order summary table row | styled-components, consistent with shipping cost row |
| Gift message textarea | Conditionally rendered below checkbox | styled-components, Theme tokens |
| Gift wrap fee on confirmation page | `cart/checkout/[orderId]/index.tsx` | styled-components, consistent with shipping cost display |

No new routes, no new providers, no new pages. The checkout form and confirmation page are extended in place.

**OpenFeature**: No new feature flags; gift wrap UI is always rendered.

---

## Telemetry impact

### New span attributes

| Service | Span | Attribute | Type | Value |
|---|---|---|---|---|
| checkout | `oteldemo.CheckoutService/PlaceOrder` | `app.order.gift_wrap` | bool | `true` if gift wrap selected, `false` otherwise |

### Existing attributes that change value

| Attribute | Effect |
|---|---|
| `app.order.amount` | Increases by gift wrap fee amount when gift_wrap=true |

### Gift wrap cost in OrderResult

`gift_wrap_cost` is stored in `OrderResult` for use in the confirmation page display. It is **not** emitted as a separate span attribute (already covered by the updated `app.order.amount`).

### Explicitly prohibited telemetry

The `gift_message` text **must never** appear in:
- Any span attribute (checkout, email, or any other service)
- Any log body or log attribute field
- Any metric label or exemplar
- Any Kafka message debug log

This rule mirrors the existing prohibition on email addresses in span attributes (`app.email.recipient` is allowed but `gift_message` is not, per the sensitive data rules).

---

## Security and sensitive data impact

Gift messages are personal/private content (may contain recipient names, personal dedications). They must be treated as PII-equivalent for observability purposes.

| Rule | Enforcement point |
|---|---|
| `gift_message` never set as span attribute | checkout (`PlaceOrder` method), email handler |
| `gift_message` never written to structured log body or attributes | checkout (slog), email (OTLP logger) |
| `gift_message` not included in Kafka `OrderResult` payload | checkout (only `gift_wrap` bool + `gift_wrap_cost` Money go into `OrderResult`) |
| `gift_message` flows only in HTTP POST to email service | checkout's `sendOrderConfirmation` HTTP payload |
| OTel Collector `transform` processor already strips query strings | no change needed to collector config |

**Threat model**: If an attacker can read the email service HTTP traffic, they see `gift_message`. This is acceptable — the email service is the intended recipient. Gift messages do not appear in Jaeger, Prometheus, or OpenSearch.

---

## Edge cases

| Case | Handling |
|---|---|
| Gift wrap checked, gift message empty | Valid; email shows no gift message section |
| Gift wrap unchecked, gift message typed | gift_wrap=false is authoritative; checkout discards gift_message before calling email |
| Currency conversion failure for gift wrap fee | Same behavior as shipping cost conversion failure — PlaceOrder returns Internal error, order not placed |
| Gift message exceeds 500 chars | Frontend validation prevents submission; no backend length check (demo scope) |
| Order placed via load-generator (synthetic) | Load generator does not need to send gift_wrap; proto3 defaults (false/"") apply |
| Gift message contains HTML/script tags | ERB template must use HTML-safe output (`<%=h gift_message %>` or `CGI.escapeHTML`) to prevent XSS in the rendered email. This is a security requirement even in the demo context since the email body is HTML. |

---

## Non-goals

- No feature flag for gift wrap enablement (always available)
- No gift wrap selection stored in cart (only captured at checkout time)
- No gift wrap tracking in accounting service logic (new proto fields available but not acted upon)
- No gift wrap line item in fraud-detection logic
- No gift message preview in the UI (just a textarea)
- No backend validation of gift message content (frontend 500-char limit only)
- No gift wrap option in `react-native-app`

---

## Acceptance criteria

1. **AC-01**: A "Add gift wrap" checkbox appears on the checkout page.
2. **AC-02**: When the checkbox is checked, a gift wrap fee line item (e.g., "$5.00" in user currency) appears in the order summary.
3. **AC-03**: When the checkbox is checked, a "Gift message (optional)" textarea appears.
4. **AC-04**: The gift wrap fee is included in the total charged to the credit card.
5. **AC-05**: The order confirmation page shows the gift wrap fee as a line item.
6. **AC-06**: The confirmation email contains the gift message when one was provided.
7. **AC-07**: The confirmation email does not contain a gift message section when no message was provided.
8. **AC-08**: `app.order.gift_wrap = true` is set on the checkout `PlaceOrder` span when gift wrap is selected.
9. **AC-09**: `app.order.gift_wrap = false` is set on the checkout `PlaceOrder` span when gift wrap is not selected.
10. **AC-10**: The gift message text does not appear in any span attribute in Jaeger.
11. **AC-11**: The gift message text does not appear in any log field in OpenSearch.
12. **AC-12**: Checkout without gift wrap completes unchanged (regression: existing PlaceOrder behavior preserved).
13. **AC-13**: For a non-USD user currency, the gift wrap fee is displayed and charged in the user's selected currency (via CurrencyService.Convert), not raw USD.

---

## Open questions

None. All ambiguities resolved as assumptions below.

---

## Assumptions

| # | Assumption | Rationale |
|---|---|---|
| A-01 | Gift wrap fee is a fixed **$5.00 USD**, converted to user currency via the existing `CurrencyService.Convert` RPC. | Simplest implementation for a teaching demo; avoids new pricing infrastructure. |
| A-02 | Gift message is optional; an empty string means "no message". | Matches request wording ("optional gift message"). |
| A-03 | If `gift_wrap = false`, the checkout service treats `gift_message` as empty regardless of what was sent. | Prevents leaking a message for an unwrapped order. |
| A-04 | `gift_message` is passed as a top-level field in the HTTP POST to the email service (not nested inside `OrderResult`). | Keeps sensitive content out of the proto-serialized `OrderResult` and the Kafka message. |
| A-05 | `OrderResult` carries `gift_wrap` (bool) and `gift_wrap_cost` (Money) so the confirmation page can display the fee without frontend-side fee reconstruction. | Avoids magic numbers in the frontend. |
| A-06 | Proto changes are backward compatible: field additions with unused field numbers only. No field renames or removals. | Prevents breaking accounting and fraud-detection consumers. |
| A-07 | No feature flag is introduced for gift wrap. The feature is always enabled. | Consistent with request scope; a flag can be added in a follow-on change. |
| A-08 | Frontend maximum gift message length is 500 characters, enforced via HTML `maxLength` attribute only (no backend enforcement). | Demo scope. |
| A-09 | Load-generator synthetic traffic does not include gift_wrap; proto3 zero defaults apply. No load-generator code change needed. | Minimises scope; gift wrap is a user-initiated action. |
| A-10 | Generated proto code is regenerated using `make docker-generate-protobuf`. The generator path is `docker-gen-proto.sh`. | Follows the documented proto generation workflow. |

---

## Human decisions

None required. Proceed to design review.
