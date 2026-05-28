# Implementation Plan: Gift Wrap at Checkout

- **Feature area**: checkout-flow
- **Change slug**: gift-wrap-checkout
- **Design doc**: [01-design.md](01-design.md)
- **Design review**: [02-design-review.md](02-design-review.md)
- **Design status**: approved

---

## 1. Architecture Summary

### Approach chosen

The gift wrap feature is implemented as an **additive, proto-first** change that threads new optional fields through the existing checkout orchestration path without modifying any service's public boundary semantics.

- Two new proto fields are added to `PlaceOrderRequest` (input) and `OrderResult` (output).
- The checkout service converts the $5 USD fee to the user's currency, adds it to the order total, and passes a sanitized `gift_message` to the email HTTP endpoint.
- The email service renders the message in its ERB template with mandatory HTML-escaping.
- The frontend threads the new fields through four TypeScript layers (IFormData → CartDetail → ApiGateway → BFF).
- The gift message text is explicitly discarded at the checkout call site when `gift_wrap=false`, preventing it from ever entering any observability signal.

### Alternatives rejected

| Alternative | Reason rejected |
|---|---|
| Store gift wrap selection in cart service | Increases coupling; cart stores line items, not checkout preferences. Design doc Non-goals. |
| Add `gift_message` to `OrderResult` proto | Would put PII in the Kafka payload and in accounting/fraud-detection consumers. Design decision: top-level HTTP POST field only. |
| Feature flag to enable/disable gift wrap | Explicit scope decision. Can be added in a follow-on change (see Non-goals in design). |
| Currency-convert the pre-order fee display | Non-goal for this iteration; "$5.00 USD" is shown pre-checkout. |
| New `GiftWrapService` | No new services allowed per CLAUDE.md unless user explicitly approves. |

---

## 2. ADRs

### ADR-01: Proto-first contract definition

**Context**: Gift wrap fields need to flow from browser to checkout to email and back to confirmation page.

**Decision**: Define `gift_wrap` and `gift_message` in `pb/demo.proto` as the canonical source of truth. Regenerate all language stubs from proto before writing implementation code. This means T-01 must complete before all other tasks.

**Consequence**: Single point of truth for field names/numbers. Stubs in Go, TypeScript, Python, C++ will be consistent. C# and Kotlin regenerate at Docker build time automatically.

---

### ADR-02: `gift_message` is a top-level HTTP field, not inside `OrderResult`

**Context**: The checkout service sends order confirmation via HTTP POST to the email service. The `OrderResult` proto struct is serialized as the `order` body field.

**Decision**: `gift_message` is passed as a top-level field in the HTTP JSON body alongside `order`, not nested inside `OrderResult`. `OrderResult` only carries `gift_wrap` (bool) and `gift_wrap_cost` (Money).

**Consequence**: `gift_message` never enters the proto serialization path, never reaches Kafka consumers (accounting, fraud-detection), and never appears in any OTLP export from OrderResult serialization.

---

### ADR-03: Checkout call-site sanitization of gift_message

**Context**: Even when `gift_wrap=false`, a browser could send a non-empty `gift_message` string.

**Decision**: In `PlaceOrder`, compute `effectiveGiftMessage` at the call site before `sendOrderConfirmation`:
```go
effectiveGiftMessage := ""
if req.GiftWrap {
    effectiveGiftMessage = req.GiftMessage
}
cs.sendOrderConfirmation(ctx, req.Email, orderResult, effectiveGiftMessage)
```

The `sendOrderConfirmation` function receives a `giftMessage string` parameter.

**Consequence**: Gift message is never forwarded to the email service on non-gift-wrap orders, regardless of what the browser sends. The sensitive string exits the checkout service only via the intended HTTP channel.

---

### ADR-04: Textarea is a new styled component, not an extension of Input

**Context**: The existing `Input` component does not support `<textarea>` elements. The existing `Input.styled.ts` uses hardcoded color strings, which is an anti-pattern.

**Decision**: Create a new `GiftMessage.styled.ts` inside `CheckoutForm/` with a styled `<textarea>` that uses Theme tokens. Do not modify `Input.tsx` or `Input.styled.ts`.

**Consequence**: No regressions in Input component usage. Styling is consistent via Theme. Component is co-located with its only consumer.

---

### ADR-05: `gift_wrap_cost` currency field must be explicitly set on the $5 literal

**Context**: `money.Sum` panics (via `money.Must`) if `CurrencyCode` fields don't match. The accumulator `total` carries `req.UserCurrency`. The $5 input literal must specify `"USD"` so `convertCurrency` returns a converted Money with `req.UserCurrency` — safe to sum.

**Decision**: Construct the fee literal as `&pb.Money{Units: 5, Nanos: 0, CurrencyCode: "USD"}`.

**Consequence**: Prevents panic at runtime for non-USD currencies. Mirrors how `price_usd` is set on proto products.

---

## 3. Services Changed

| Service | Language | Owner agent | Nature of change |
|---|---|---|---|
| `pb/demo.proto` | protobuf | go-implementer | Add fields to `PlaceOrderRequest` and `OrderResult`; add `reserved 4` |
| checkout | Go | go-implementer | PlaceOrder: currency convert gift wrap fee, sum into total, set span attributes, sanitize gift_message, update sendOrderConfirmation signature |
| email | Ruby | ruby-implementer | Extract gift_message from HTTP body; pass to ERB locals; render in confirmation.erb with CGI.escapeHTML |
| frontend | TypeScript/Next.js | typescript-frontend-implementer | IFormData types, CheckoutForm.tsx, CartItems.tsx, CartDetail.tsx, ApiGateway.ts, BFF checkout.ts, confirmation page |

---

## 4. Contracts Changed

### `pb/demo.proto`

**`PlaceOrderRequest`** — field additions:
```protobuf
reserved 4;           // guard: prevents accidental reuse of pre-existing gap
bool   gift_wrap    = 7;
string gift_message = 8;
```

**`OrderResult`** — field additions:
```protobuf
bool  gift_wrap      = 6;
Money gift_wrap_cost = 7;
```

Both changes are **backward compatible** — existing consumers that ignore the new fields continue working with proto3 zero defaults (false, "", nil Money).

### HTTP `POST /send_order_confirmation` body

Before: `{ "email": "...", "order": {...} }`  
After: `{ "email": "...", "order": { ..., "gift_wrap": true, "gift_wrap_cost": {...} }, "gift_message": "..." }`

`gift_wrap: false` is **omitted** from the serialized JSON due to proto3 `omitempty` on bool. Ruby `OpenStruct` returns `nil` for missing keys — all guards must handle `nil`.

### Frontend BFF `POST /api/checkout`

Two new optional body fields: `gift_wrap: boolean` (default false), `gift_message: string` (default "").

---

## 5. Frontend / UI-Kit Changes

| Component | File | Change |
|---|---|---|
| `CheckoutForm` | `src/frontend/components/CheckoutForm/CheckoutForm.tsx` | Add gift wrap checkbox (labelled, with `htmlFor`/`id`). Conditionally **mount** (not CSS-hide) the gift message textarea when checked. Own `giftWrap` and `giftMessage` state; lift to `IFormData`. |
| `GiftMessage.styled.ts` (new) | `src/frontend/components/CheckoutForm/GiftMessage.styled.ts` | Styled `<textarea>` using Theme tokens. `maxLength={500}`. |
| `CartItems` | `src/frontend/components/CartItems/CartItems.tsx` | Show gift wrap fee row ("$5.00") alongside shipping row when `giftWrap=true`. |
| `IFormData` / `CartDetail` / `ApiGateway` | Multiple files | Thread `gift_wrap` and `gift_message` through four layers. |
| BFF | `src/frontend/pages/api/checkout.ts` | Forward `gift_wrap` and `gift_message` to gRPC PlaceOrder. |
| Confirmation page | `src/frontend/pages/cart/checkout/[orderId]/index.tsx` | Render gift wrap fee line item from `OrderResult.gift_wrap_cost`; include `gift_wrap_cost` in `orderTotal` useMemo. |

**No new routes. No new providers. No new pages.**

**Accessibility**: Both checkbox and textarea must have explicit `<label htmlFor>` / `id` pairing.

**Styling constraint**: Use only `Theme` tokens. Reference `Checkout.styled.ts` for the established pattern. Do NOT copy hardcoded colors from `Input.styled.ts`.

---

## 6. Telemetry Changes

### New span attributes on `oteldemo.CheckoutService/PlaceOrder`

| Attribute | Type | Rule |
|---|---|---|
| `app.order.gift_wrap` | bool | Set on **every** order (true or false) |
| `app.order.gift_wrap.amount` | float64 | Set **only** when `gift_wrap=true`. Same format as `app.shipping.amount`. |

### New span event

`span.AddEvent("gift_wrap_fee_applied")` — emitted after successful gift wrap fee currency conversion.

### Changed attribute value

`app.order.amount` — will include the gift wrap fee amount when gift_wrap=true.

### Prohibited telemetry (gift_message text must never appear in)

- Span attributes (any service)
- Span events (including the existing `"prepared"` event)
- Structured log body or attribute fields (checkout slog, email OTLP logger)
- Metric labels or exemplars
- Kafka message debug logs
- Stdout / debug output

---

## 7. Sensitive Data Handling

`gift_message` is PII-equivalent personal text. Enforcement:

1. **Checkout call-site sanitization** (ADR-03): message zeroed out when `gift_wrap=false`.
2. **Not passed to `sendOrderConfirmation` unless gift_wrap=true**.
3. **Not in `OrderResult`** — only `gift_wrap` (bool) + `gift_wrap_cost` (Money) go into the proto struct.
4. **Email service**: message passes through HTTP POST body only, rendered in ERB with `CGI.escapeHTML`. Never set as span attribute.
5. **Error handler**: the email service `error do` block must not be modified to log request bodies or rendered email content.
6. **BFF** (`src/frontend/pages/api/checkout.ts`): `giftMessage` / `gift_message` must NOT appear in any `console.log`, span attribute, or request body log. Next.js does not log request bodies by default — do not change that default behavior.

---

## 8. Test Strategy

### Unit tests (TDD — write before implementation)

**T-02 (checkout)**:
- `TestPlaceOrder_GiftWrapIncludesConvertedFeeInTotal` — when gift_wrap=true, verify total = items + shipping + converted_gift_wrap_fee
- `TestPlaceOrder_GiftWrapFalseExcludesFeeFromTotal` — when gift_wrap=false, total unchanged
- `TestPlaceOrder_GiftMessageNotInSpanAttributes` — gift_message not present as span attribute
- `TestPlaceOrder_GiftWrapSpanAttributeAlwaysSet` — `app.order.gift_wrap` set for both true/false orders
- `TestSendOrderConfirmation_GiftMessageOmittedWhenFalse` — effectiveGiftMessage is "" when gift_wrap=false

**T-03 (email)**:
- `test_gift_wrap_confirmation_email` — POST with gift_message results in message in rendered ERB
- `test_no_gift_message_section_when_absent` — POST without gift_message renders no message section
- `test_gift_message_xss_escaped` — `<script>` tag in gift_message is HTML-escaped in output
- `test_nil_gift_wrap_handled_gracefully` — missing gift_wrap key (nil from OpenStruct) treated as false

**T-04 (frontend)**:
- Unit test: `CheckoutForm` renders checkbox; checking checkbox mounts textarea
- Unit test: unchecking checkbox unmounts textarea (message state cleared)
- Unit test: `ApiGateway.placeOrder` includes `gift_wrap` and `gift_message` in POST body

### Trace-based tests

Add `test/tracetesting/checkout/checkout_gift_wrap.yaml` (note: place inside
`test/tracetesting/checkout/` — not at the root `test/tracetesting/` level, where it would
not be discovered). After creating the file, add it to
`test/tracetesting/checkout/all.yaml` so it runs in the suite:

  - Verify `app.order.gift_wrap` attribute present on PlaceOrder span
  - Verify `gift_wrap_fee_applied` span event present when gift_wrap=true
  - Verify no span attribute named `gift_message` anywhere in the trace

**AC-09 gap** — `app.order.gift_wrap=false` on standard orders has no automated trace test
in the new yaml above (it only tests the gift_wrap=true path). To close this gap, add a new
assertion to `test/tracetesting/checkout/place-order.yaml`: assert that
`app.order.gift_wrap` attribute is present and equals `false` on the baseline PlaceOrder span.

**F-28 note** — T-02 (Go) and T-03 (Ruby) run in parallel but share the JSON contract for
`POST /send_order_confirmation`. Each implementer must self-verify against the design: Go must
confirm the marshalled `gift_message` key matches exactly the key the Ruby OpenStruct reads.
There is no machine-checked schema; verify by inspecting the HTTP body in the trace or logs.

---

## 9. Manual / Browser Verification

See [verification/manual-test-cases.md](verification/manual-test-cases.md) for full steps.

Key paths:
1. Happy path: gift wrap selected + message typed → email received, total correct, fee on confirmation page
2. Gift wrap selected, no message → confirmation page shows fee, email has no message section
3. Gift wrap not selected → total unchanged, no fee on page, email unchanged
4. Non-USD currency user → fee converted, confirmation page shows converted amount
5. Regression: standard checkout still works

---

## 10. Trace / Observability Verification

In Jaeger, after a gift-wrap order:

1. Find span `oteldemo.CheckoutService/PlaceOrder` — should have:
   - `app.order.gift_wrap = true`
   - `app.order.gift_wrap.amount` (float64, non-zero)
   - `app.order.amount` (includes gift wrap fee)
   - Event `gift_wrap_fee_applied`
2. Confirm `gift_message` text does NOT appear in any span attribute or event value
3. Confirm `app.order.gift_wrap = false` for a non-gift-wrap order

---

## 11. Task Breakdown

Tasks are ordered by dependency. T-02 and T-03 can run in parallel after T-01. T-04 and T-05 are sequential (same service).

| ID | Title | Owner agent | Status | Depends on |
|---|---|---|---|---|
| T-01 | Update pb/demo.proto and regenerate all language stubs | go-implementer | todo | — |
| T-02 | Implement gift wrap logic in checkout service (Go) | go-implementer | todo | T-01 |
| T-03 | Implement gift message rendering in email service (Ruby) | ruby-implementer | todo | T-01 |
| T-04 | Frontend: checkout form gift wrap UI + state threading | typescript-frontend-implementer | todo | T-01 |
| T-05 | Frontend: confirmation page gift wrap fee display | typescript-frontend-implementer | todo | T-04 |

### Parallel execution plan

```
T-01 (proto) ──┬──→ T-02 (checkout Go)
               ├──→ T-03 (email Ruby)
               └──→ T-04 (frontend form) ──→ T-05 (frontend confirmation)
```

After T-01 completes: launch T-02 and T-03 in parallel, and T-04 in parallel with them.
After T-04 completes: launch T-05.
T-02 and T-03 have no internal dependency and can complete independently.

---

## 12. Definition of Done

All of the following must be true before claiming completion:

- [ ] All 5 task evidence files exist in `tasks/`
- [ ] `spec-compliance-reviewer` passed on all tasks
- [ ] `observability-reviewer` passed (gift_message never in telemetry; app.order.gift_wrap always set)
- [ ] `security-data-leak-reviewer` passed (gift_message PII handling)
- [ ] `test-verification-reviewer` passed on all tasks
- [ ] All 14 acceptance criteria verified (AC-01 through AC-14)
- [ ] Trace-based test `test/tracetesting/checkout/checkout_gift_wrap.yaml` written and added to `test/tracetesting/checkout/all.yaml`
- [ ] `test/tracetesting/checkout/place-order.yaml` updated with `app.order.gift_wrap=false` assertion (AC-09 gap)
- [ ] Manual browser verification completed (see manual-test-cases.md)
- [ ] `final-verification-report.md` exists with verdict `pass`

### Finalization docs to update

- [ ] `docs/features/checkout-flow/overview.md` — PlaceOrder sequence, new span attributes (`app.order.gift_wrap`, `app.order.gift_wrap.amount`), new span event (`gift_wrap_fee_applied`), source files changed (CheckoutForm.tsx, CartItems.tsx, GiftMessage.styled.ts, CartDetail.tsx, confirmation page)
- [ ] `docs/features/order-confirmation-email.md` — new HTTP POST body field (`gift_message`); updated `sendOrderConfirmation` signature
- [ ] `docs/ai-knowledge/services/checkout.md` — gift wrap fee logic, `sendOrderConfirmation` signature change, new span attributes, `effectiveGiftMessage` sanitization pattern
- [ ] `docs/ai-knowledge/services/email.md` — `gift_message` local in ERB template; `require 'cgi'` dependency; test infrastructure (rack-test + minitest added to Gemfile)
- [ ] `docs/ai-knowledge/communication/http-map.md` — updated `POST /send_order_confirmation` body shape (new `gift_message` top-level field; `OrderResult` now carries `gift_wrap` + `gift_wrap_cost`)
- [ ] `docs/ai-knowledge/communication/overview.md` — note that the `gift_message` field is added to the email HTTP contract; acknowledge backward-compat claim alongside the existing atomic-redeploy note for field changes
- [ ] `docs/ai-knowledge/observability/overview.md` — new `app.order.gift_wrap` (bool, always-set) and `app.order.gift_wrap.amount` (float64, gift_wrap=true only) attributes; `gift_wrap_fee_applied` span event; `gift_message` PII rule (never in span attributes, events, or logs)

---

## 13. Evidence Requirements

| File | Created by |
|---|---|
| `tasks/T-01.evidence.md` | go-implementer (T-01 execution) |
| `tasks/T-02.evidence.md` | go-implementer (T-02 execution) |
| `tasks/T-03.evidence.md` | ruby-implementer (T-03 execution) |
| `tasks/T-04.evidence.md` | typescript-frontend-implementer (T-04 execution) |
| `tasks/T-05.evidence.md` | typescript-frontend-implementer (T-05 execution) |
| `verification/final-verification-report.md` | sdd-verify stage |
| `.sdd/evidence/latest-spec-review-pass` | spec-compliance-reviewer |
| `.sdd/evidence/latest-code-quality-pass` | code-quality-reviewer |
| `.sdd/evidence/latest-verification-pass` | sdd-verify stage |

---

## 14. Rollback / Failure Handling

### If T-01 (proto) fails

Stop. Do not proceed to any other task. The regenerated stubs are the foundation for all downstream changes. Fix the proto edit and re-run `make docker-generate-protobuf` before continuing.

### If T-02 (checkout Go) fails

The checkout service will not compile. Orders without gift wrap continue to work if the previous binary is still running (feature is additive). Fix and re-run Go tests before proceeding to review.

### If T-03 (email Ruby) fails

Email service will fail to start or return 500 on order confirmation. The checkout service will log an HTTP error at the email call site but the order itself is still placed (email failure is non-fatal per existing behavior). Fix and re-run Ruby tests.

### If T-04 or T-05 (frontend) fails

The frontend will fail to compile or render. All checkout functionality is broken. Fix TypeScript compilation errors. Roll back by reverting the frontend changes if compilation cannot be fixed quickly.

### Production rollback path

Since all proto changes are backward compatible (additive only), reverting only the frontend or only the checkout service is safe at the proto level. Reverting `pb/demo.proto` requires redeploying all services that use the generated stubs — this is the nuclear option. Use service-level rollbacks first.
