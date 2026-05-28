# Iteration Log

Accepted knowledge updates, in reverse chronological order.

| Date | Agent | Target File | Change Type | Summary |
|------|-------|-------------|-------------|---------|
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout finalize) | docs/ai-knowledge/observability/overview.md | addition | Added gift_message PII rule (Rule 6) to Sensitive Data Rules section |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout finalize) | docs/ai-knowledge/observability/detail.md | addition | Added gift_message PII rule (Rule 8) to Sensitive Data Rules section |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout finalize) | docs/ai-knowledge/communication/http-map.md | correction | Fixed stale line number for checkout→email POST: main.go:561 → main.go:604 |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout finalize) | docs/ai-knowledge/communication/proto-contracts.md | correction | Fixed stale line number for checkout→email POST: main.go:561 → main.go:604 |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout finalize) | docs/features/checkout-flow/detail.md | addition | Created detail.md with full behavioral spec, contracts, telemetry, edge cases, PII rules, tests, source paths |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/services/checkout.md | addition | Gift wrap proto fields, span attrs, event, sendOrderConfirmation signature, PII constraint |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/services/frontend.md | addition | IFormData gift wrap fields, CartItems prop, confirmation page, CypressFields enum additions |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/services/email.md | addition | HTTP body with gift_message, CGI.escapeHTML, email_server_test.rb in source files |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/observability/detail.md | addition | Checkout span attrs app.order.gift_wrap, app.order.gift_wrap.amount, gift_wrap_fee_applied event |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/communication/proto-contracts.md | addition | PlaceOrderRequest fields 7-8 and OrderResult fields 6-7 for gift wrap |
| 2026-05-27 | sdd-orchestrator (gift-wrap-checkout execute) | docs/ai-knowledge/communication/http-map.md | addition | Email HTTP server endpoint and checkout outbound client updated with gift_message body |
| 2026-05-27 | knowledge-curator (bootstrap) | docs/ai-knowledge/ (all) | addition | Initial bootstrap: extracted all service, communication, observability, frontend, and feature docs from source |
| 2026-05-27 | knowledge-curator (bootstrap) | docs/ai-knowledge/services/service-inventory.json | addition | Created machine-readable service inventory for 28 services |
| 2026-05-27 | knowledge-curator (bootstrap) | docs/features/ | addition | Created feature behavior docs for product-browsing, checkout-flow, product-reviews, recommendations, order-confirmation-email, and feature-flags |

---

*Append new entries here after each accepted update. Newest first.*

*Format: `| {date} | {agent} | {target file} | correction\|addition\|deprecation | {one-line summary} |`*
