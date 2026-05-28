# Browser Manual Verification Report: Gift Wrap Checkout

- **Feature area**: checkout-flow
- **Change slug**: gift-wrap-checkout
- **Date**: 2026-05-27
- **Tool**: agent-browser CLI
- **App URL**: http://localhost:8080
- **Verifier**: browser-verification agent

---

## Setup Notes

The `Add To Cart` button on product pages does not trigger observable Next.js client-side navigation in the agent-browser headless environment (the React `push('/cart')` fires but the browser automation does not follow SPA navigation after the async mutation). The Add To Cart API call does execute successfully (verified via cart service logs showing `AddItemAsync` calls). Cart items were seeded via:

1. `agent-browser eval` to set `localStorage.setItem('session', JSON.stringify({userId: 'verify-session-001', currencyCode: 'USD'}))`
2. `curl -X POST http://localhost:8080/api/cart` with `userId: 'verify-session-001'` and `productId: 'OLJCESPC7Z'`
3. `agent-browser open http://localhost:8080/cart` to load the cart with the item

This workaround correctly reflects the app's session behavior (localStorage-based userId) and does not bypass any gift-wrap logic.

---

## TC-01: Gift wrap checkbox visible on checkout form

**URL visited**: http://localhost:8080/cart

**Steps performed:**
1. Seeded cart with product OLJCESPC7Z (National Park Foundation Explorascope, $101.96) for session `verify-session-001`
2. Navigated to http://localhost:8080/cart
3. Scrolled checkout form past the credit card section using `scrollintoview` on the checkbox element
4. Verified gift wrap checkbox presence and default state via accessibility tree snapshot

**Expected result:** "Add gift wrap (+$5.00)" checkbox visible and unchecked by default

**Actual result:** Checkbox `Add gift wrap (+$5.00)` is present in the checkout form, positioned after the CVV/credit card section. The checkbox is unchecked by default (`checked=false` in accessibility tree).

**Screenshot:** `screenshots/TC-01-gift-wrap-checkbox.png`

**Verdict: PASS**

---

## TC-02: Gift wrap fee row in order summary

**URL visited**: http://localhost:8080/cart

**Steps performed:**
1. On the cart page with product in cart (same session as TC-01)
2. Clicked the gift wrap checkbox to check it
3. Scrolled to the order summary section

**Expected result:** A "Gift Wrap" fee row appears alongside Shipping row; dollar amount shown; total increases

**Actual result:**
- Before checking: Total showed `$ 110.95` (product $101.96 + shipping $8.99)
- After checking: Order summary shows three rows:
  - Shipping: $8.99
  - **Gift Wrap: $5.00** (new row appeared alongside Shipping)
  - Total: $115.95 (increased by exactly $5.00)

**Screenshot:** `screenshots/TC-02-gift-wrap-fee-row.png`

**Verdict: PASS**

---

## TC-03: Gift message textarea mounts/unmounts

**URL visited**: http://localhost:8080/cart

**Steps performed:**
1. Confirmed no textarea present in unchecked state (accessibility tree snapshot showed no `Gift message (optional)` textbox)
2. Checked the gift wrap checkbox
3. Verified "Gift message (optional)" textarea appeared in DOM
4. Typed "Hello from browser test" in the textarea via `fill`
5. Unchecked the gift wrap checkbox
6. Verified textarea absent from DOM (accessibility tree snapshot)
7. Re-checked the gift wrap checkbox
8. Verified fresh empty textarea appeared in DOM

**Expected result:**
- Textarea absent when unchecked (unmounted, not CSS-hidden)
- Textarea present with label "Gift message (optional)" when checked
- Textarea disappears when unchecked (removed from DOM)
- Fresh empty textarea on re-check (message cleared)

**Actual result:**
- Unchecked state: no `textbox "Gift message (optional)"` in accessibility tree — confirmed absent from DOM
- After checking: `textbox "Gift message (optional)" [ref=e30]` appeared in DOM
- Filled textarea accepted input "Hello from browser test"
- After unchecking: `textbox "Gift message (optional)"` completely absent from accessibility tree (unmounted, not CSS-hidden)
- After re-checking: Fresh `textbox "Gift message (optional)"` appeared with no value (previous message cleared — confirms unmount/remount)

**Screenshot:** `screenshots/TC-03-gift-message-textarea.png`

**Verdict: PASS**

---

## TC-04: Happy path — place order with gift wrap and confirm

**URL visited**: http://localhost:8080/cart then http://localhost:8080/cart/checkout/[orderId]

**Steps performed:**
1. Cart loaded with product (National Park Foundation Explorascope, $101.96)
2. Checked gift wrap checkbox
3. Typed gift message: "Happy Birthday from the team!"
4. Filled CVV: 672 (credit card 4432-8015-6152-0454, expiry January/2030, email someone@example.com, address 1600 Amphitheatre Parkway already pre-filled)
5. Clicked "Place Order" button
6. Order completed; page transitioned to confirmation

**Expected result:**
- Redirected to confirmation page URL matching `/cart/checkout/`
- "Gift Wrap:" line item visible in order summary on confirmation page
- Total on confirmation page includes gift wrap amount

**Actual result:**
- Final URL: `http://localhost:8080/cart/checkout/d7a66f30-59c2-11f1-8c15-267bed248587?order=...`
- URL matches `/cart/checkout/[orderId]` pattern
- Confirmation page shows "Your order is complete!" and "We've sent you a confirmation email."
- Order summary on confirmation page:
  - National Park Foundation Explorascope: $101.96 (qty 1)
  - Shipping: $8.99
  - **Gift Wrap: $5.00** (line item present)
  - **Total: $115.95**
- Order query parameter in URL contains `giftWrap: true` and `giftWrapCost: {currencyCode: "USD", units: 5, nanos: 0}`

**Screenshot:** `screenshots/TC-04-confirmation-page.png`

**Verdict: PASS**

---

## Summary

| TC | Title | Verdict |
|---|---|---|
| TC-01 | Gift wrap checkbox visible on checkout form | PASS |
| TC-02 | Gift wrap fee row in order summary | PASS |
| TC-03 | Gift message textarea mounts/unmounts | PASS |
| TC-04 | Happy path — place order with gift wrap and confirm | PASS |

**Overall verdict: PASS**

Cases passed: 4  
Cases failed: 0  
Cases blocked: 0

---

## Suspected Bugs

None identified. All tested behaviors match the acceptance criteria.

---

## Observations

1. The agent-browser `click` on the "Add To Cart" button fires the React onClick handler (verified via cart service logs showing `AddItemAsync` calls) but the resulting `router.push('/cart')` SPA navigation is not followed by agent-browser snapshots. This is a tooling limitation, not an app bug. Workaround: seed cart via API + localStorage injection.

2. The confirmation page correctly reads `gift_wrap_cost` from the `OrderResult` passed via URL query parameter. The `orderTotal` useMemo correctly sums items + shipping + gift_wrap_cost, matching the charged amount ($115.95).

3. The textarea is truly conditionally mounted (not CSS-hidden): it disappears from the accessibility tree entirely when unchecked, and reappears fresh (empty) when re-checked.

---

## Recommended E2E Tests

1. **Cypress/Playwright**: `checkout_gift_wrap.cy.ts` — Full happy path: add product, check gift wrap, fill message, place order, assert confirmation page shows Gift Wrap line item and correct total.

2. **Cypress/Playwright**: `checkout_no_gift_wrap_regression.cy.ts` — Standard checkout without gift wrap: verify no Gift Wrap row in order summary, total matches items + shipping only.

3. **Cypress/Playwright**: `gift_wrap_textarea_mount.cy.ts` — Verify textarea mounts when checkbox checked, unmounts when unchecked, and message is cleared on re-check.

4. **Trace test**: `test/tracetesting/checkout/checkout_gift_wrap.yaml` — After placing order with gift wrap: assert `app.order.gift_wrap=true`, `app.order.gift_wrap.amount` present, `gift_wrap_fee_applied` span event present, no `gift_message` span attribute.

---

## Screenshots Written

- `screenshots/TC-01-gift-wrap-checkbox.png` — Gift wrap checkbox unchecked, positioned after credit card section
- `screenshots/TC-02-gift-wrap-fee-row.png` — Order summary showing Gift Wrap $5.00 fee row alongside Shipping, updated Total $115.95
- `screenshots/TC-03-gift-message-textarea.png` — Gift message textarea with label "Gift message (optional)" containing typed text
- `screenshots/TC-04-confirmation-page.png` — Confirmation page order summary showing Gift Wrap $5.00 and Total $115.95
