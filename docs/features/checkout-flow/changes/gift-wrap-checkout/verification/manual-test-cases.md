# Manual Test Cases: Gift Wrap at Checkout

**Feature area**: checkout-flow  
**Change slug**: gift-wrap-checkout  
**AC coverage**: AC-01 through AC-14

---

## Prerequisites

- Docker Compose stack running: `docker compose up --build`
- Browser pointed at: `http://localhost:8080`
- Jaeger UI open at: `http://localhost:16686`
- (Optional) OpenSearch Dashboards at: `http://localhost:5601`

---

## TC-01: Gift wrap checkbox visible on checkout form (AC-01)

**Steps:**
1. Add any product to the cart.
2. Navigate to the cart page.
3. Click "Place Order" or navigate to the checkout page.
4. Scroll to the checkout form.

**Expected:**
- An "Add gift wrap (+$5.00)" checkbox is visible in the checkout form.
- The checkbox is unchecked by default.

---

## TC-02: Gift wrap fee row appears in order summary (AC-02)

**Steps:**
1. Add any product to the cart. Navigate to checkout.
2. Check the "Add gift wrap (+$5.00)" checkbox.

**Expected:**
- A "Gift Wrap" fee row appears in the order summary alongside the shipping row.
- The fee shows "$5.00" (USD).
- The order total in the summary increases by $5.00.

---

## TC-03: Gift message textarea conditionally mounted (AC-03)

**Steps:**
1. Navigate to checkout.
2. Check the gift wrap checkbox.
3. Observe the form.
4. Uncheck the gift wrap checkbox.
5. Observe the form.

**Expected:**
- After step 2: A "Gift message (optional)" textarea appears below the checkbox.
- After step 4: The textarea disappears (not CSS-hidden — visually absent from the DOM).
- If you re-check, a fresh empty textarea appears (previous message is cleared).

---

## TC-04: Happy path — gift wrap + message, confirmed total (AC-04, AC-05, AC-06)

**Steps:**
1. Add a product to the cart.
2. Navigate to checkout. Fill in all required fields (address, email, credit card).
3. Check "Add gift wrap".
4. Type a gift message: `"Happy Birthday from the team!"`.
5. Click "Place Order".

**Expected:**
- The order completes successfully and you are redirected to the confirmation page.
- The confirmation page shows a "Gift Wrap" fee line item with the converted amount (in user's currency).
- The confirmation page `Order Total` includes the gift wrap fee (total = items + shipping + gift wrap).
- The user receives a confirmation email (or the email service logs show a sent email) containing the gift message: `"Happy Birthday from the team!"`.

---

## TC-05: Gift wrap selected, no message (AC-07 — no message section in email)

**Steps:**
1. Navigate to checkout. Check "Add gift wrap". Leave the gift message textarea empty.
2. Place the order.

**Expected:**
- Order completes successfully.
- Confirmation page shows gift wrap fee line item.
- Confirmation email does NOT contain a "Gift Message" section.

---

## TC-06: Gift wrap not selected — no fee, no message (AC-07, AC-12 regression)

**Steps:**
1. Navigate to checkout. Leave the gift wrap checkbox unchecked.
2. Place the order normally.

**Expected:**
- No gift wrap fee row in the order summary.
- Order total unchanged (items + shipping only).
- Confirmation page: no gift wrap fee line item.
- Confirmation email: no gift message section.
- This is the regression test — existing checkout behavior fully preserved (AC-12).

---

## TC-07: Non-USD currency — fee converted (AC-13)

**Steps:**
1. Change the site currency to EUR (or any non-USD currency) using the currency selector.
2. Add a product to the cart. Navigate to checkout.
3. Check "Add gift wrap".
4. Place the order.

**Expected:**
- The gift wrap fee displayed on the checkout form still shows "$5.00" (pre-order USD display; note: converted display is a non-goal for this iteration).
- The confirmation page shows the gift wrap cost in the user's selected currency (converted by the checkout service via CurrencyService.Convert).
- The `orderTotal` on the confirmation page is in the user's currency and includes the converted gift wrap fee.

---

## TC-08: Telemetry check — Jaeger (AC-08, AC-09, AC-10)

**Steps:**
1. Place an order **with** gift wrap (TC-04).
2. Open Jaeger at `http://localhost:16686`.
3. Search for service: `checkout`, operation: `oteldemo.CheckoutService/PlaceOrder`.
4. Open the trace for the completed order.
5. Inspect span attributes.
6. Place an order **without** gift wrap (TC-06).
7. Repeat Jaeger inspection.

**Expected (gift wrap = true order):**
- Span attribute `app.order.gift_wrap` = `true`
- Span attribute `app.order.gift_wrap.amount` is present (non-zero float)
- Span event `gift_wrap_fee_applied` is present
- NO span attribute with key `gift_message` or containing the message text (AC-10)

**Expected (gift wrap = false order):**
- Span attribute `app.order.gift_wrap` = `false`
- NO span attribute `app.order.gift_wrap.amount`
- NO span event `gift_wrap_fee_applied`
- NO span attribute containing the message text (AC-10)

---

## TC-09: XSS safety — gift message HTML escaping (AC-14)

**Steps:**
1. Navigate to checkout. Check "Add gift wrap".
2. Type in the gift message textarea: `<script>alert("xss")</script>`
3. Place the order.

**Expected:**
- The confirmation email body contains the literal text `&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;` (HTML-escaped).
- No JavaScript popup or browser alert fires when the email is viewed.
- The raw `<script>` tag does NOT appear unescaped in the email source.

---

## TC-10: Telemetry check — gift message not in logs (AC-11)

**Steps:**
1. Place an order with gift wrap and a recognizable message (e.g., `"UniqueTestMessage12345"`).
2. Open OpenSearch Dashboards at `http://localhost:5601` (or check raw OTLP logs).
3. Search for `UniqueTestMessage12345`.

**Expected:**
- Zero results: the gift message text does not appear in any log record body, log attribute, or span attribute in OpenSearch.

---

## TC-11: Confirmation page total matches charged amount (AC-05 strict)

**Steps:**
1. Add a $10.00 product to the cart. Note the shipping cost shown (e.g., $8.00).
2. Check gift wrap.
3. Place the order.
4. On the confirmation page, verify:
   - Items subtotal = $10.00
   - Shipping = (quoted amount)
   - Gift Wrap = (converted fee)
   - Order Total = items + shipping + gift wrap

**Expected:**
- The sum of displayed line items equals the displayed `Order Total`.
- No discrepancy (previously the total could exclude gift wrap cost, causing a visible mismatch).

---

## Acceptance Criteria Coverage Summary

| AC | Test Case |
|---|---|
| AC-01: Gift wrap checkbox visible | TC-01 |
| AC-02: Fee row appears when checked | TC-02 |
| AC-03: Textarea conditionally mounted | TC-03 |
| AC-04: Gift wrap fee charged | TC-04 |
| AC-05: Confirmation page total correct | TC-04, TC-11 |
| AC-06: Email contains message | TC-04 |
| AC-07: No message section when absent | TC-05, TC-06 |
| AC-08: app.order.gift_wrap=true in Jaeger | TC-08 |
| AC-09: app.order.gift_wrap=false in Jaeger | TC-08 |
| AC-10: Gift message not in span attributes | TC-08 |
| AC-11: Gift message not in logs | TC-10 |
| AC-12: Regression — standard checkout | TC-06 |
| AC-13: Non-USD currency converted | TC-07 |
| AC-14: XSS escaped in email | TC-09 |
