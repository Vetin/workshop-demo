# Reviewer Routing Reference

For each type of code change, which reviewers the orchestrator must dispatch.

Last updated: 2026-05-27

---

## Routing Table

| Change Type | Mandatory Reviewers | Conditional Reviewers |
|-------------|--------------------|-----------------------|
| Any service code change | observability-reviewer, docs-consistency-reviewer, security-data-leak-reviewer, technical-{language}-reviewer for the affected service | test-verification-reviewer (if new OTel spans are added or span names change) |
| `pb/demo.proto` change | service-contract-reviewer, ALL 12 language technical reviewers | — |
| `src/frontend/` change | technical-typescript-reviewer, frontend-ui-kit-reviewer | — |
| `src/otel-collector/` change | observability-reviewer, infra-otel-implementer review (re-check pipeline config) | docs-consistency-reviewer (if pipeline topology changes) |
| `src/flagd/demo.flagd.json` change | docs-consistency-reviewer, observability-reviewer | domain experts for all services that consume the changed flags |
| Cross-service communication change (new call, removed call, protocol change) | service-contract-reviewer | — |
| Kafka schema change | service-contract-reviewer, domain-checkout-expert, domain-accounting-expert, domain-fraud-detection-expert | — |
| New feature implementation | test-verification-reviewer | feature-documenter (creates docs/features/ entry after review passes) |
| `docker-compose.yml` or `k8s/` change | infra-otel-implementer review, docs-consistency-reviewer | observability-reviewer (if collector or exporter config changes) |
| Generated proto stub change (`.pb.go`, `_pb2.py`, `*_grpc.*`) | service-contract-reviewer | technical-{language}-reviewer for the language whose stubs changed |
| `docs/ai-knowledge/` change | docs-consistency-reviewer | knowledge-curator (if doc content contradicts code) |
| Bug fix (existing span/metric changes) | observability-reviewer, technical-{language}-reviewer | test-verification-reviewer (mandatory if the bug was a telemetry regression) |
| New service added | service-boundary-mapper (re-run), observability-reviewer, docs-consistency-reviewer, service-contract-reviewer | All domain experts for services that communicate with the new service |

---

## Reviewer Dispatch Order

When multiple reviewers apply, dispatch in this order to avoid wasted re-runs:

1. **observability-reviewer** — catches the most common blocking issues (incorrect span names, missing attributes, wrong semantic conventions)
2. **security-data-leak-reviewer** — checks PII; if a blocker is found here, stop other reviews until fixed
3. **service-contract-reviewer** — if proto changed; blockers here affect all language reviewers
4. **technical-{language}-reviewer** — language-specific correctness and idioms
5. **frontend-ui-kit-reviewer** — only for frontend changes
6. **test-verification-reviewer** — coverage check; runs last so it can see the final span names
7. **docs-consistency-reviewer** — final check after all code reviews pass
8. **feature-documenter** — writes docs/features/ entry only after all above pass

---

## Notes

- "infra-otel-implementer review" in the table means the orchestrator re-reads the changed config with the infra-otel-implementer as a read-only consultant, not a code writer.
- For `pb/demo.proto` changes, all 12 technical reviewers must run because all services depend on the proto. This is the most expensive review scenario.
- `feature-documenter` is a knowledge-maintainer, not a reviewer — it does not block completion, but it must run after the implementation is accepted.
- `domain-{service}-expert` as a conditional reviewer means: dispatch it when the orchestrator needs deeper service-specific context to arbitrate conflicting reviewer findings, not as a default gating step.
