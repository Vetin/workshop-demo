# Proposed Knowledge Updates

Pending proposals awaiting knowledge-curator review.

*When a proposal is accepted, move it to `iteration-log.md` with status `[ACCEPTED]`.*
*When a proposal is rejected, move it to `rejected-updates.md` with status `[REJECTED]`.*

---

## [ACCEPTED] 2026-05-27 — sdd-orchestrator (gift-wrap-checkout)

**Patterns that worked well:**

1. **Proto-first with generated code in T-01** — separating proto + generated
   code into a dedicated task before any service code meant every subsequent
   implementer had correct type signatures from the start. Zero proto-mismatch
   rework across all 5 tasks.

2. **PII enforcement as a named constraint** — making "gift_message must never
   appear in telemetry" an explicit named constraint in the design (and repeating
   it in every task brief) meant zero PII leakage findings across all reviewers.
   The constraint propagated cleanly through all 5 tasks.

3. **TDD in checkout service (T-02)** — tests were written before the
   implementation. This caught the currency code mismatch in the `money.Sum`
   call before it could cause a runtime panic in production.

4. **Conditional mounting vs. CSS-hiding (T-04)** — the domain reviewer caught
   that the original plan said "hide" the textarea; the correct behavior is
   "unmount" so that unchecking clears the message. This was caught at design
   review and avoided a subtle UX + state management bug.

5. **Cypress tests via Docker** — the local Cypress 15.8.2 binary had a macOS
   ARM verification bug (`--no-sandbox` rejected). Running via
   `cypress/included:14.5.0` Docker image (the project's canonical method) was
   a clean fallback. Document this pattern in the testing runbook.

**Patterns that caused rework:**

1. **camelCase vs. snake_case in IFormData (T-04)** — the T-04 implementer
   initially used `gift_wrap` and `gift_message` in `IFormData` (snake_case),
   inconsistent with every other field in the interface (camelCase). The domain
   and TypeScript reviewers caught this; a comprehensive rename was applied.
   **Lesson**: Include an explicit `IFormData` field naming convention in the
   frontend service ai-knowledge doc.

2. **Cypress tests visiting `/cart` with empty cart (verification)** — the T-04
   tests used `cy.visit('/cart')` directly; the cart page renders `<EmptyCart />`
   when there are no items, so the checkout form (with gift wrap checkbox) was
   never shown. Tests 2-5 failed. The fix was to add the add-to-cart navigation
   preamble that test 6 already used.
   **Lesson**: Cypress tests that need form UI must always ensure cart has items.
   Document this in the Cypress testing patterns section.

3. **Stale line number in http-map.md** — `src/checkout/main.go:561` was the
   pre-implementation line for `sendOrderConfirmation`. After refactoring the
   function signature (adding `giftMessage string` param), the call moved to
   line 604. The docs-consistency-reviewer caught this during finalization.
   **Lesson**: Line-number citations in ai-knowledge docs go stale with
   refactoring. Prefer function-name references when possible, or treat line
   numbers as approximate guides only.

4. **`$15.00` vs `$ 15.00` in Confirmation.cy.ts** — the total assertion used
   `$15.00` but `ProductPrice` renders `$ 15.00` (space between symbol and
   amount). The test failed during E2E execution.
   **Lesson**: Document the `ProductPrice` rendering format in the frontend
   ai-knowledge doc. Future test authors should know to use `$ N.NN` format.

*(No pending proposals.)*

---

## How to add a proposal

Append a new entry in this format:

```markdown
## [PENDING] {YYYY-MM-DD} — {proposing-agent}

**Target file:** docs/ai-knowledge/...
**Change type:** correction | addition | deprecation
**Source evidence:** src/{service}/{file}:{line}

**Current text:**
> (exact quote from the current doc, or "missing")

**Proposed text:**
> (replacement or addition)

**Justification:**
One sentence explaining what changed in the code and why this doc update is needed.
```
