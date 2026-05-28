# E2E Test Plan: Gift Wrap at Checkout

## Feature area

checkout-flow

## Change slug

gift-wrap-checkout

## Source manual verification report

docs/features/checkout-flow/changes/gift-wrap-checkout/verification/browser-manual-verification-report.md

---

## Coverage Matrix

| TC | Description | Decision | Rationale |
|---|---|---|---|
| TC-01 | Gift wrap checkbox visible on checkout form | COVERED | `Checkout.cy.ts` — `shows gift wrap checkbox on checkout page` |
| TC-02 | Gift wrap fee row appears in order summary | COVERED | `Checkout.cy.ts` — `gift wrap fee row appears in cart summary when gift wrap is checked` |
| TC-03 | Gift message textarea conditionally mounted | COVERED | `Checkout.cy.ts` — two tests covering mount on check and unmount + clear on uncheck |
| TC-04 | Happy path — gift wrap + message, confirmed total | NEEDS_E2E | POST body fields are verified; full confirmation page assertion (line item + total arithmetic) is not. See E2E-01. |
| TC-05 | Gift wrap selected, no message | NEEDS_E2E | No test verifies the empty-message submission path and its confirmation page output. See E2E-02. |
| TC-06 | Standard order regression (no gift wrap) | NEEDS_E2E | `Confirmation.cy.ts` covers the confirmation page; the full submit-to-confirmation round trip for a standard order is not covered by any existing Cypress test. See E2E-03. |
| TC-07 | Non-USD currency fee converted | SKIP_E2E | Requires the currency selector to persist across a real checkout round-trip through the backend currency service. Currency conversion is backend logic; a frontend-only Cypress test cannot verify the converted amount without a live running stack, making it inherently environment-dependent and flaky. Covered by Go unit test `TestPlaceOrder_GiftWrapIncludesConvertedFeeInTotal`. |
| TC-08 | Telemetry — Jaeger span attributes | SKIP_E2E | Requires Jaeger UI or OTLP collector. Not accessible to Cypress. Covered by trace-based test `test/tracetesting/checkout/checkout_gift_wrap.yaml`. |
| TC-09 | XSS safety — gift message HTML escaping | SKIP_E2E | XSS escaping is server-side rendering in the Ruby email ERB template. Cypress cannot open a rendered email. Covered by Ruby unit test `test_gift_message_xss_escaped`. |
| TC-10 | Gift message not in logs | SKIP_E2E | Requires OpenSearch / OTLP log sink query. Not accessible to Cypress. Covered by observability-reviewer audit and Go unit test `TestPlaceOrder_GiftMessageNotInSpanAttributes`. |
| TC-11 | Confirmation page total matches charged amount | COVERED | `Confirmation.cy.ts` — `shows gift wrap fee row when order included gift wrap` asserts `$15.00` total (shipping $10 + gift wrap $5, zero items in fixture). Arithmetic correctness is verified. |

---

## Candidate E2E Cases

### E2E-01

#### Based on manual case

TC-04

#### Acceptance criteria covered

AC-04, AC-05, AC-06 (partial — email not verifiable in Cypress)

#### Why E2E is justified

TC-04 is the acceptance-criteria-critical happy path: gift wrap selected, message typed, order placed, confirmation page reflects the fee line item and the correct total. The existing `gift wrap fields included in checkout POST body` test only intercepts the request body — it does not wait for the confirmation page to render or assert its contents. Completing this path end-to-end through the browser is user-visible, regression-prone, and crosses the frontend BFF boundary into the confirmation page rendering layer.

#### Test location

`src/frontend/cypress/e2e/Checkout.cy.ts` — add inside existing `describe('Checkout Flow')` block

#### Test approach

1. Add a product to the cart (using the same `addToCart` + `getCart` intercept + wait pattern already established in the existing `should create an order with two items` test).
2. Check the gift wrap checkbox.
3. Type a gift message into the textarea.
4. Click Place Order; wait for `@placeOrder` to resolve.
5. Assert the URL matches `/checkout/`.
6. Assert `cy.contains('Gift Wrap:')` is visible on the confirmation page.
7. Assert the displayed total is greater than the subtotal (arithmetic precision is already covered by `Confirmation.cy.ts` with the fixture approach; here we assert presence and non-zero fee, not exact cents — the exact-cents assertion is in `Confirmation.cy.ts` with a known fixture).

#### Selectors / roles

- `CypressFields.GiftWrapCheckbox` — existing enum value
- `CypressFields.GiftMessageTextarea` — existing enum value
- `CypressFields.CheckoutPlaceOrder` — existing enum value
- `cy.contains('Gift Wrap:')` — stable text content

#### Test data

- First product card in the catalog (same as existing test — deterministic because products are seeded)
- Gift message: `'Happy Birthday from the team!'`

#### Commands to run

```
cd src/frontend && npx cypress run --spec "cypress/e2e/Checkout.cy.ts"
```

#### Status

planned

#### Skip/block reason

N/A

---

### E2E-02

#### Based on manual case

TC-05

#### Acceptance criteria covered

AC-07 (no gift message section in email is not assertable in Cypress, but confirmation page shows gift wrap fee with no message-related errors)

#### Why E2E is justified

TC-05 covers an edge case that is distinct from TC-04: gift wrap is selected but the textarea is left empty. This is a separate code path in the BFF (`giftMessage: ""` in the POST body) and in the confirmation page render (gift wrap line item present, no message to display). It is regression-prone because a naive implementation might crash or omit the fee row when the message is empty.

#### Test location

`src/frontend/cypress/e2e/Checkout.cy.ts` — add inside existing `describe('Checkout Flow')` block

#### Test approach

1. Add a product to cart (same intercept pattern).
2. Check the gift wrap checkbox.
3. Leave the gift message textarea empty (do not type).
4. Click Place Order; wait for `@placeOrder`.
5. Assert URL matches `/checkout/`.
6. Assert `cy.contains('Gift Wrap:')` is visible.
7. Intercept assertion: verify `request.body.giftWrap === true` and `request.body.giftMessage === ''`.

#### Selectors / roles

- `CypressFields.GiftWrapCheckbox`
- `CypressFields.CheckoutPlaceOrder`
- `cy.contains('Gift Wrap:')`

#### Test data

- First product card in the catalog
- No gift message (textarea left empty)

#### Commands to run

```
cd src/frontend && npx cypress run --spec "cypress/e2e/Checkout.cy.ts"
```

#### Status

planned

#### Skip/block reason

N/A

---

### E2E-03

#### Based on manual case

TC-06

#### Acceptance criteria covered

AC-07, AC-12

#### Why E2E is justified

TC-06 is the regression guard: a standard order (no gift wrap) must not show a gift wrap row anywhere in the flow. `Confirmation.cy.ts` already asserts the confirmation page renders no gift wrap row from a crafted fixture. What is missing is the submit-to-confirmation round trip through the actual checkout POST — the regression guard that the BFF does not accidentally inject `giftWrap: true` by default, and that the confirmation page does not show a spurious row when the order query param has `giftWrap: false`.

The crafted-fixture test in `Confirmation.cy.ts` covers the render side. This test covers the submit side.

#### Test location

`src/frontend/cypress/e2e/Checkout.cy.ts` — add inside existing `describe('Checkout Flow')` block

#### Test approach

1. Add a product to cart (same intercept pattern).
2. Leave the gift wrap checkbox unchecked.
3. Click Place Order; wait for `@placeOrder`.
4. Assert URL matches `/checkout/`.
5. Assert `cy.contains('Gift Wrap:')` does not exist on the confirmation page.
6. Intercept assertion: verify `request.body.giftWrap === false` (or absent).

#### Selectors / roles

- `CypressFields.CheckoutPlaceOrder`
- `cy.contains('Gift Wrap:')` — asserted `.should('not.exist')`

#### Test data

- First product card in the catalog
- No gift wrap interaction

#### Commands to run

```
cd src/frontend && npx cypress run --spec "cypress/e2e/Checkout.cy.ts"
```

#### Status

planned

#### Skip/block reason

N/A

---

## E2E Tests Added

None in this plan execution. The three NEEDS_E2E cases (E2E-01, E2E-02, E2E-03) are **planned but not yet written**. They should be authored in `src/frontend/cypress/e2e/Checkout.cy.ts` following the implementation of the feature tasks.

The two existing Cypress files that already contain the covered tests are:

- `src/frontend/cypress/e2e/Checkout.cy.ts` — five gift wrap tests added (TC-01, TC-02, TC-03 checkout-side, and the POST body assertion for TC-04)
- `src/frontend/cypress/e2e/Confirmation.cy.ts` — two gift wrap confirmation tests added (TC-11 and TC-06 render-side)

---

## E2E Tests Intentionally Not Added

| TC | Reason |
|---|---|
| TC-07 (non-USD currency) | Backend currency conversion requires a live running stack with the currency service. The converted amount cannot be asserted deterministically without knowing the exchange rate in use at test time. Covered by Go unit test `TestPlaceOrder_GiftWrapIncludesConvertedFeeInTotal`. Defer to a dedicated integration-test tier if one is introduced. |
| TC-08 (Jaeger span attributes) | Requires Jaeger HTTP API or OTLP sink access. Not reachable from Cypress. Covered by `test/tracetesting/checkout/checkout_gift_wrap.yaml` (trace-based test). |
| TC-09 (XSS escaping) | HTML escaping is performed in the Ruby email ERB template; Cypress cannot open or inspect rendered emails. Covered by Ruby unit test `test_gift_message_xss_escaped`. If an email-rendering integration test is introduced in the future, this should be revisited. |
| TC-10 (gift message not in logs) | Requires querying OpenSearch or an OTLP log collector. Not reachable from Cypress. Covered by Go unit tests and observability-reviewer audit. |

---

## Commands Run

None — this is a planning document. Tests listed as `planned` have not yet been executed.

---

## Summary

**Total manual test cases**: 11

**Breakdown by decision**:

| Decision | Count | TCs |
|---|---|---|
| COVERED (existing Cypress) | 5 | TC-01, TC-02, TC-03, TC-11, and TC-06 confirmation-render |
| NEEDS_E2E (planned, not yet written) | 3 | TC-04, TC-05, TC-06 submit-side |
| SKIP_E2E (non-browser tooling required) | 4 | TC-07, TC-08, TC-09, TC-10 |

**E2E coverage gaps after planned tests are written**: None for browser-verifiable acceptance criteria. All four SKIP_E2E cases are covered by the appropriate non-browser test tier (Go unit tests, Ruby unit tests, trace-based tests).

**Follow-up tasks**:

1. Write E2E-01 in `src/frontend/cypress/e2e/Checkout.cy.ts` — happy path with gift wrap + message, confirm Gift Wrap line item on confirmation page.
2. Write E2E-02 in `src/frontend/cypress/e2e/Checkout.cy.ts` — gift wrap selected with empty message, confirm fee row present.
3. Write E2E-03 in `src/frontend/cypress/e2e/Checkout.cy.ts` — standard order regression, confirm no Gift Wrap row on confirmation page and `giftWrap: false` in POST body.
4. Once E2E-01 through E2E-03 are written, run the full Cypress suite and record results in this document under "Commands Run" and "Result".
5. TC-07 (non-USD currency) should be revisited if an integration-test tier backed by a live stack is introduced. The test would assert: confirmation page shows gift wrap fee in user's selected currency with the correct converted amount.
