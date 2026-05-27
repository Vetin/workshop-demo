# Change Design

## Metadata

- feature area: checkout-flow
- change slug: gift-wrap-checkout
- request type: feature
- status: approved
- created by: sdd-orchestrator
- reviewed by: sdd-orchestrator (consolidated 9 reviewers)
- approved by: sdd-orchestrator

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
2. NEW: "Add gift wrap (+$5.00)" checkbox is shown in CheckoutForm, alongside a
   gift wrap fee row ($5.00 USD, pre-order display) in the CartItems order summary.
   Note: the $5.00 is displayed in USD at this stage; the confirmed converted amount
   appears on the confirmation page from OrderResult.gift_wrap_cost.
3. User checks the gift wrap checkbox
   → Gift wrap fee row becomes visible in order summary ($5.00 USD)
   → "Gift message (optional)" textarea is conditionally mounted below the checkbox
4. User optionally types a gift message (max 500 chars, frontend validation only)
5. User clicks "Place Order"
6. Frontend BFF (pages/api/checkout.ts):
   - Reads gift_wrap (bool) and gift_message (string) from request body
   - Passes them to CheckoutService.PlaceOrder via gRPC
   - TypeScript chain: IFormData → CartDetail.onPlaceOrder → ApiGateway.placeOrder
     → BFF → gRPC PlaceOrder (all four surfaces carry the new fields)
7. Checkout service (PlaceOrder):
   a. Reads gift_wrap and gift_message from PlaceOrderRequest
   b. If gift_wrap=true: convert &pb.Money{Units:5, Nanos:0, CurrencyCode:"USD"}
      via cs.convertCurrency(ctx, ..., req.UserCurrency). This call happens in
      PlaceOrder directly, AFTER prepareOrderItemsAndShippingQuoteFromCart returns
      and BEFORE chargeCard is called, using the existing cs.convertCurrency helper.
      Emit span.AddEvent("gift_wrap_fee_applied") after successful conversion.
   c. If gift_wrap=true: add the converted giftWrapCostLocalized to total via
      money.Must(money.Sum(total, giftWrapCostLocalized))
   d. Constructs OrderResult with gift_wrap and gift_wrap_cost fields populated
   e. Charges card for updated total (includes gift wrap fee when applicable)
   f. Sets span attributes: app.order.gift_wrap (bool), app.order.gift_wrap.amount
      (float64, same format as app.shipping.amount; only set when gift_wrap=true)
   g. Does NOT set any span attribute, span event, or log field for gift_message text
   h. Compute effectiveGiftMessage at the call site:
        effectiveGiftMessage := ""
        if req.GiftWrap { effectiveGiftMessage = req.GiftMessage }
      Then call: cs.sendOrderConfirmation(ctx, req.Email, orderResult, effectiveGiftMessage)
      The updated signature is sendOrderConfirmation(ctx, email, giftMessage string,
      order *pb.OrderResult). Include gift_message in the JSON body only when non-empty.
   i. Publishes OrderResult to Kafka (gift_wrap + gift_wrap_cost included; gift_message
      is NOT in OrderResult and does NOT reach the Kafka payload)
8. Email service (POST /send_order_confirmation):
   - Receives JSON: { "email": "...", "order": {..., "gift_wrap": true,
     "gift_wrap_cost": {...} }, "gift_message": "..." }
   - Note: gift_wrap: false is OMITTED from the JSON due to proto3 omitempty on bool;
     the Ruby side sees nil (not false) for non-gift-wrap orders — guards must handle nil
   - Handler updates: erb(:confirmation, locals: { order: data.order,
     gift_message: data.gift_message }) — gift_message MUST be passed as a local
   - ERB template: conditional section using nil+empty guard:
     <% unless gift_message.nil? || gift_message.empty? %>
     with HTML-safe output: <%= CGI.escapeHTML(gift_message) %>
   - Does NOT set any span attribute for gift_message text
9. User sees order confirmation page:
   - Shows gift wrap fee as a line item using gift_wrap_cost from OrderResult
   - The orderTotal useMemo MUST include gift_wrap_cost to match the charged amount
   - gift_wrap_cost is available on the query.order object via IProductCheckout
```

---

## Services touched

| Service | Language | What changes |
|---|---|---|
| **frontend** | TypeScript/Next.js | (1) `CheckoutForm.tsx`: add gift wrap checkbox + gift message textarea (state lives here, lifted to `CartDetail.tsx`). (2) `CartItems.tsx`: add gift wrap fee row alongside shipping row. (3) `cart/checkout/[orderId]/index.tsx`: add gift wrap fee line item; update `orderTotal` useMemo to include `gift_wrap_cost`. (4) `IFormData` (CheckoutForm): add `gift_wrap: boolean`, `gift_message: string`. (5) `CartDetail.tsx` `onPlaceOrder` callback: thread new fields. (6) `ApiGateway.placeOrder`: propagate new fields. (7) `pages/api/checkout.ts` BFF route: pass fields to gRPC. |
| **checkout** | Go | `PlaceOrder`: read `gift_wrap`/`gift_message`; if gift_wrap=true convert `&pb.Money{Units:5, Nanos:0, CurrencyCode:"USD"}` via `cs.convertCurrency`; add to `total` before `chargeCard`; set `app.order.gift_wrap` (bool) and `app.order.gift_wrap.amount` (float64) span attributes; discard `gift_message` at call site when `gift_wrap=false`; update `sendOrderConfirmation` signature to include `giftMessage string`; populate `OrderResult` gift fields. |
| **email** | Ruby/Sinatra | (1) HTTP handler: extract `data.gift_message` from JSON payload. (2) `send_email` function: update `erb(:confirmation, locals: { order: data.order, gift_message: data.gift_message })`. (3) `confirmation.erb`: add conditional gift message section with nil+empty guard and `CGI.escapeHTML`. |
| **pb/demo.proto** | protobuf | `PlaceOrderRequest`: add `gift_wrap` (bool, field 7), `gift_message` (string, field 8), and `reserved 4` (guard against accidental reuse of gap field). `OrderResult`: add `gift_wrap` (bool, field 6) and `gift_wrap_cost` (Money, field 7). |
| **Generated code** | Go, TypeScript, others | Regenerate with `make docker-generate-protobuf`: `src/checkout/genproto/`, `src/frontend/protos/demo.ts`, `src/react-native-app/protos/demo.ts` (no logic changes in react-native-app), Python stubs, C++ stubs. C# (accounting) and Kotlin (fraud-detection) stubs regenerate automatically at Docker build time from `pb/demo.proto` — no manual step needed, container rebuild is sufficient. |

---

## Contracts touched

### 1. `pb/demo.proto` — gRPC contract (HIGH RISK — affects all language stubs)

**`PlaceOrderRequest`** — add two fields and guard the pre-existing gap:
```protobuf
message PlaceOrderRequest {
    string user_id = 1;
    string user_currency = 2;
    Address address = 3;
    reserved 4;                    // guard: field 4 was previously used, prevent reuse
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

**Generated code that must be regenerated** (via `make docker-generate-protobuf`):
- Go: `src/checkout/genproto/oteldemo/` (checkout uses PlaceOrderRequest + OrderResult)
- TypeScript: `src/frontend/protos/demo.ts` (frontend calls PlaceOrder, reads OrderResult)
- TypeScript: `src/react-native-app/protos/demo.ts` (regenerate; no logic change in app)
- Python: `src/recommendation/demo_pb2*.py`, `src/product-reviews/demo_pb2*.py` (regenerate; no logic change needed)
- C++: `src/currency/build/generated/proto/` (regenerate; no logic change needed)
- Node.js runtime (payment): loaded at runtime from `pb/demo.proto`; no explicit code change needed

**C# and Kotlin consumers (Kafka):** accounting and fraud-detection regenerate their proto stubs **automatically at Docker build time** from the copied `pb/demo.proto` in their respective Dockerfiles. No manual `make docker-generate-protobuf` needed for these services — a container rebuild is sufficient. Proto3 new optional fields default to zero/false. No code changes required unless those services choose to act on the new `gift_wrap` field.

**JSON serialization note:** `sendOrderConfirmation` uses `encoding/json` to marshal `*pb.OrderResult`. Proto-generated Go structs include `json:"field_name,omitempty"` struct tags that produce snake_case JSON keys (verified by existing working fields: `order_id`, `shipping_tracking_id`, etc.). New fields `gift_wrap` and `gift_wrap_cost` will carry `json:"gift_wrap,omitempty"` and `json:"gift_wrap_cost,omitempty"` tags after regeneration — consistent with existing fields. **Important:** `gift_wrap: false` is OMITTED from the serialized JSON due to `omitempty` on a bool. The Ruby `OpenStruct` parser yields `nil` (not `false`) for absent keys — the ERB template guard must handle both nil and empty string.

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

### Component architecture

Gift wrap UI spans two existing components with state lifted to `CartDetail.tsx`:

| Element | Owner component | Notes |
|---|---|---|
| Gift wrap checkbox + label | `CheckoutForm.tsx` | Inside the `<form>` element; state via `IFormData` |
| Gift message textarea | `CheckoutForm.tsx` | Conditionally **mounted** (not CSS-hidden) when checkbox is checked; unmounting clears the typed message, consistent with the edge case that unchecking discards the message |
| Gift wrap fee row | `CartItems.tsx` | Rendered alongside shipping row; displays "$5.00" (USD pre-order display) |
| Gift wrap fee on confirmation page | `cart/checkout/[orderId]/index.tsx` | Reads `gift_wrap_cost` from `OrderResult`; `orderTotal` useMemo must add `gift_wrap_cost.units/nanos` to avoid total mismatch |

State flow: `CheckoutForm` owns `giftWrap: boolean` and `giftMessage: string` local state → lifted as props to `CartDetail.tsx` → threaded into `onPlaceOrder` → `ApiGateway.placeOrder`.

**TypeScript surfaces requiring changes:**
1. `IFormData` in `CheckoutForm.tsx` — add `gift_wrap: boolean`, `gift_message: string`
2. `CartDetail.tsx` `onPlaceOrder` callback signature — accept new fields
3. `ApiGateway.placeOrder` — propagate new fields in POST body
4. `pages/api/checkout.ts` BFF — forward to gRPC PlaceOrder (TypeScript types update after proto regeneration)

### Styling

All new elements must use `Theme` tokens (colors, sizes). Reference `Checkout.styled.ts` for the existing pattern. `Input.styled.ts` has hardcoded colors (`#f9f9f9`, `#cacaca`) — do NOT copy this anti-pattern.

The gift message **textarea** is not supported by the existing `Input` component. A new styled textarea primitive is required (either a new variant in `Input.tsx` or a standalone `Textarea.styled.ts`), sharing the same border/background styling as `Input.styled.ts`.

### Accessibility

- Gift wrap checkbox: `<label htmlFor="gift_wrap">` with matching `id="gift_wrap"` on the input
- Gift message textarea: `<label htmlFor="gift_message">` with matching `id="gift_message"` on the textarea

### Pre-order fee display

The gift wrap fee is displayed as **"$5.00"** (USD) at checkout time. Currency-converted pre-order display is a non-goal for this iteration (see Non-goals). The confirmed converted amount is shown on the confirmation page from `OrderResult.gift_wrap_cost`.

No new routes, no new providers, no new pages.

**OpenFeature**: No new feature flags; gift wrap UI is always rendered.

---

## Telemetry impact

### New span attributes

| Service | Span | Attribute | Type | Notes |
|---|---|---|---|---|
| checkout | `oteldemo.CheckoutService/PlaceOrder` | `app.order.gift_wrap` | bool | `true`/`false` on every order. `gift_wrap` is a single compound terminal token (matching `card_type` precedent), not two dot-separated sub-concepts. |
| checkout | `oteldemo.CheckoutService/PlaceOrder` | `app.order.gift_wrap.amount` | float64 | Same format as `app.shipping.amount`. Set only when `gift_wrap=true`. Enables cost decomposition in traces independent of `app.order.amount`. |

### Recommended span event

After successful gift wrap fee currency conversion, emit:
```
span.AddEvent("gift_wrap_fee_applied")
```
This makes traces useful for debugging currency conversion failures specific to gift wrap, and has pedagogical value in the workshop context.

### Existing attributes that change value

| Attribute | Effect |
|---|---|
| `app.order.amount` | Increases by gift wrap fee amount when gift_wrap=true |

### Metrics / adoption rate observability

`app.order.gift_wrap` is a **span attribute only** — it does not become a Prometheus metric dimension. The current `spanmetrics` connector has no `dimensions` config and does not promote custom span attributes to metric labels. Gift wrap adoption rate is therefore **not queryable as a time-series metric** from the existing collector pipeline. If a counter metric for adoption rate is desired, a dedicated `app.checkout.gift_wrap.selected` counter can be added in a follow-on iteration.

### Explicitly prohibited telemetry

The `gift_message` text **must never** appear in:
- Any span attribute (checkout, email, or any other service)
- Any span event (including the existing `"prepared"` span event on the checkout span)
- Any log body or log attribute field (checkout slog, email OTLP logger)
- Any metric label or exemplar
- Any Kafka message debug log
- Any stdout `puts` / debug output

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

**Email service error handler risk:** The email service's `error do` block calls `record_exception(env['sinatra.error'])`. If Pony or another component raises an exception whose message string embeds the rendered email body (which contains the gift message), the exception span attribute would capture it. Implementation requirement: the `error do` handler must not be extended to log request bodies or rendered content; any exception that wraps a mail failure must strip the body text before `record_exception` is called.

---

## Edge cases

| Case | Handling |
|---|---|
| Gift wrap checked, gift message empty | Valid; email shows no gift message section |
| Gift wrap unchecked, gift message typed | gift_wrap=false is authoritative; checkout discards gift_message before calling email |
| Currency conversion failure for gift wrap fee | Same behavior as shipping cost conversion failure — PlaceOrder returns Internal error, order not placed |
| Gift message exceeds 500 chars | Frontend validation prevents submission; no backend length check (demo scope) |
| Order placed via load-generator (synthetic) | Load generator does not need to send gift_wrap; proto3 defaults (false/"") apply |
| Gift message contains HTML/script tags | ERB template must use `<%= CGI.escapeHTML(gift_message) %>` (NOT `<%=h %>` — `h` is a Rails helper not available in Sinatra). `CGI` is Ruby stdlib. This is a mandatory security requirement: the email body is HTML. |
| `gift_message` absent from JSON payload (nil, not "") | `JSON.parse(..., object_class: OpenStruct)` returns `nil` for missing keys. The ERB guard must be: `unless gift_message.nil? \|\| gift_message.empty?`. Also: `gift_wrap: false` is omitted from the JSON due to proto3 `omitempty` on bool, so `data.order.gift_wrap` is `nil` for non-gift-wrap orders — the template and handler must treat nil as false. |

---

## Non-goals

- No feature flag for gift wrap enablement (always available). Note: this demo explicitly teaches feature flags as an observability mechanism — skipping a flag here is a deliberate scope decision. A rollout flag can be added in a follow-on iteration.
- No gift wrap selection stored in cart (only captured at checkout time)
- No gift wrap tracking in accounting service logic (new proto fields available but not acted upon)
- No gift wrap line item in fraud-detection logic
- No gift message preview in the UI (just a textarea)
- No backend validation of gift message content (frontend 500-char limit only)
- No gift wrap option in `react-native-app`
- No currency-converted pre-order fee display. The gift wrap fee is shown as "$5.00" (USD) at checkout time. The confirmed converted amount appears on the confirmation page from `OrderResult.gift_wrap_cost`. A converted pre-order display can be added in a follow-on iteration using the existing BFF currency convert pattern.

---

## Acceptance criteria

1. **AC-01**: A "Add gift wrap" checkbox appears on the checkout page.
2. **AC-02**: When the checkbox is checked, a gift wrap fee line item ("$5.00") appears in the order summary.
3. **AC-03**: When the checkbox is checked, a "Gift message (optional)" textarea appears.
4. **AC-04**: The gift wrap fee is included in the total charged to the credit card.
5. **AC-05**: The order confirmation page shows the gift wrap fee as a line item, and the displayed total matches the charged amount (i.e., `orderTotal` includes `gift_wrap_cost`).
6. **AC-06**: The confirmation email contains the gift message when one was provided.
7. **AC-07**: The confirmation email does not contain a gift message section when no message was provided (or when gift_wrap=false).
8. **AC-08**: `app.order.gift_wrap = true` is set on the checkout `PlaceOrder` span when gift wrap is selected.
9. **AC-09**: `app.order.gift_wrap = false` is set on the checkout `PlaceOrder` span when gift wrap is not selected.
10. **AC-10**: The gift message text does not appear in any span attribute or span event in Jaeger.
11. **AC-11**: The gift message text does not appear in any log field or log body in OpenSearch.
12. **AC-12**: Checkout without gift wrap completes unchanged (regression: existing PlaceOrder behavior preserved).
13. **AC-13**: For a non-USD user currency, the gift wrap fee is charged in the user's selected currency (CurrencyService.Convert applied); the converted amount appears on the confirmation page from `gift_wrap_cost`.
14. **AC-14**: The gift message in the confirmation email uses HTML-safe output; a `<script>` tag in the input does not appear unescaped in the rendered email body.

---

## Open questions

None. All ambiguities resolved as assumptions below.

---

## Assumptions

| # | Assumption | Rationale |
|---|---|---|
| A-01 | Gift wrap fee is a fixed **$5.00 USD**, converted to user currency via the existing `CurrencyService.Convert` RPC. | Simplest implementation for a teaching demo; avoids new pricing infrastructure. |
| A-02 | Gift message is optional; an empty string means "no message". | Matches request wording ("optional gift message"). |
| A-03 | If `gift_wrap = false`, the checkout service treats `gift_message` as empty. The guard is enforced **in `PlaceOrder` at the call site**, before `sendOrderConfirmation` is invoked: `effectiveMsg := ""; if req.GiftWrap { effectiveMsg = req.GiftMessage }`. This prevents the sensitive string from ever entering `sendOrderConfirmation` when gift wrap is false. | Prevents leaking a message for an unwrapped order. |
| A-04 | `gift_message` is passed as a top-level field in the HTTP POST to the email service (not nested inside `OrderResult`). | Keeps sensitive content out of the proto-serialized `OrderResult` and the Kafka message. |
| A-05 | `OrderResult` carries `gift_wrap` (bool) and `gift_wrap_cost` (Money) so the confirmation page can display the fee without frontend-side fee reconstruction. | Avoids magic numbers in the frontend. |
| A-06 | Proto changes are backward compatible: field additions with unused field numbers only. No field renames or removals. | Prevents breaking accounting and fraud-detection consumers. |
| A-07 | No feature flag is introduced for gift wrap. The feature is always enabled. | Consistent with request scope; a flag can be added in a follow-on change. |
| A-08 | Frontend maximum gift message length is 500 characters, enforced via HTML `maxLength` attribute only (no backend enforcement). | Demo scope. |
| A-09 | Load-generator synthetic traffic does not include gift_wrap; proto3 zero defaults apply. No load-generator code change needed. | Minimises scope; gift wrap is a user-initiated action. |
| A-10 | Generated proto code is regenerated using `make docker-generate-protobuf`. The generator path is `docker-gen-proto.sh`. | Follows the documented proto generation workflow. |
| A-11 | The $5.00 gift wrap fee input Money is constructed as `&pb.Money{Units: 5, Nanos: 0, CurrencyCode: "USD"}`. The `CurrencyCode` field must be set explicitly. | `money.Sum` panics via `money.Must` on mismatching currency codes; the `total` accumulator uses `req.UserCurrency`. The converted result carries `req.UserCurrency`, safe to sum. Matches the `price_usd` pattern for product prices in the proto. |

---

## Docs to update at finalization

These docs are stale after implementation and must be updated at `/sdd-finalize`:

| Doc | What to update |
|---|---|
| `docs/features/checkout-flow/overview.md` | Add `app.order.gift_wrap` and `app.order.gift_wrap.amount` to span attributes list; add gift wrap fee to PlaceOrder call sequence; add `CheckoutForm.tsx` and `CartItems.tsx` to source paths |
| `docs/features/order-confirmation-email.md` | Update HTTP contract table: `{ email, order }` → `{ email, order, gift_message }` |
| `docs/ai-knowledge/observability/overview.md` | Add `app.order.gift_wrap` and `app.order.gift_wrap.amount` to span attribute conventions |

---

## Human decisions

None required. Design approved after review.
