# Validation Categories

All dimensions along which a code change is validated in the SDD harness.

Last updated: 2026-05-27

---

## Category List

### 1. Code Quality
**What it checks:** Idiomatic language usage, error handling patterns, naming conventions, code structure, readability, and avoidance of anti-patterns for the target language/runtime.

**Checked by:** `technical-{language}-reviewer` for the relevant language.

**Examples of findings:**
- Go: not using idiomatic error wrapping with `fmt.Errorf("%w", err)`
- Python: using bare `except:` instead of typed exception handling
- TypeScript: missing return type annotations on exported functions
- Rust: using `.unwrap()` in production paths instead of `?` propagation

---

### 2. Service Architecture
**What it checks:** Whether the change respects service boundary definitions — no new services added without explicit approval, no service reaching into another service's data store directly, no cross-service imports.

**Checked by:** `docs-consistency-reviewer`, `sdd-orchestrator` (as policy enforcer).

**Project rule:** Do not add new services unless the user explicitly approves it (CLAUDE.md).

---

### 3. Project Rules
**What it checks:** Compliance with the rules in CLAUDE.md:
- No hidden telemetry-impacting changes
- No modifications to generated files unless the generator path is documented
- No claiming completion without local verification evidence
- Keeping project knowledge in docs/ai-knowledge/
- Keeping feature behavior in docs/features/

**Checked by:** `docs-consistency-reviewer`.

---

### 4. Domain Behavior
**What it checks:** Whether the service-specific business logic is correct. For example: currency conversion math in currency service, cart item merging logic in cart service, fee calculation in checkout service.

**Checked by:** `domain-{service}-expert` for the specific service that changed.

**When dispatched:** Conditionally — when the orchestrator needs to verify logic correctness or arbitrate a conflicting reviewer finding, not as a default gating step.

---

### 5. Technical Correctness by Language/Runtime
**What it checks:** Language-specific correctness beyond style — correct use of OTel SDK for that language, proper goroutine/thread management, memory safety patterns, correct gRPC client/server patterns for the runtime.

**Checked by:** `technical-{language}-reviewer`.

**Distinction from Code Quality (category 1):** Code Quality is about style and idioms; Technical Correctness is about whether the code will behave correctly at runtime.

---

### 6. Distributed Flow
**What it checks:** Cross-service call chains — whether trace context is propagated correctly across service boundaries, whether new service-to-service calls follow the established communication topology.

**Checked by:** `service-contract-reviewer` (when proto changes); `communication-flow-mapper` output used as reference.

**Note:** This category overlaps with Observability (category 8) for trace propagation. Both apply when a new cross-service call is added.

---

### 7. Service Contract Compatibility
**What it checks:** Whether protobuf/gRPC changes in `pb/demo.proto` are backward-compatible, whether all generated stubs in all languages are regenerated and consistent, and whether no caller service is broken by a field rename or type change.

**Checked by:** `service-contract-reviewer`.

**Trigger:** Any change to `pb/demo.proto` or any generated stub file (`.pb.go`, `_pb2.py`, `*_grpc.rb`, `demo_pb.js`, etc.).

---

### 8. Observability
**What it checks:** OTel instrumentation correctness across all services:
- Span names follow OTel semantic conventions
- Required span attributes are present (e.g., `rpc.method`, `db.statement`, `http.route`)
- Custom attribute names follow the project's naming scheme
- Metric instrument types are correct (counter vs. histogram vs. gauge)
- Trace context is propagated via W3C TraceContext headers
- No spans are created and immediately abandoned (orphaned spans)

**Checked by:** `observability-reviewer`.

**Frequency:** Runs after every service code change — mandatory, not conditional.

---

### 9. Security / Data Leakage
**What it checks:** Whether personally identifiable information (PII) appears in span attributes or log bodies:
- User email addresses in spans
- Credit card numbers or payment details in attributes
- User session tokens or auth headers in spans
- Unmasked postal addresses or phone numbers in logs

**Checked by:** `security-data-leak-reviewer`.

**Frequency:** Runs after every service code change — mandatory, not conditional.

---

### 10. Frontend / UI-Kit Consistency
**What it checks:** Whether frontend changes follow the established design system:
- Styled-components using theme tokens (not hardcoded hex colors or pixel values)
- Accessibility (a11y) attributes present on interactive elements
- OTel browser instrumentation patterns (user interaction spans, page load spans)
- Component structure consistent with the existing UI kit patterns

**Checked by:** `frontend-ui-kit-reviewer`.

**Trigger:** Any change under `src/frontend/`.

---

### 11. Testing / Verification Evidence
**What it checks:**
- Trace tests in `test/tracetesting/` cover new spans introduced by the implementation
- Cypress e2e tests cover new user-visible behavior
- Local verification evidence exists in `.sdd/evidence/`
- Test assertions use the correct span names and attribute keys (not stale names from before the change)

**Checked by:** `test-verification-reviewer`.

**Trigger:** Any new OTel spans added, any span names changed, or any change to `test/tracetesting/`.

---

### 12. Documentation Consistency
**What it checks:** Whether docs/ai-knowledge/ files accurately describe the code as it currently exists:
- Service descriptions match actual service behavior
- Communication flow maps reflect actual inter-service calls
- Port numbers and protocol types are correct
- No docs describe behavior that was removed or refactored

**Checked by:** `docs-consistency-reviewer`, `knowledge-curator` (writer), `docs-consistency-reviewer` (verifier).

**Frequency:** Runs after every implementation as a final gate, and after knowledge-curator updates docs.

---

### 13. Knowledge Update Quality
**What it checks:** Whether the docs update produced by knowledge-curator is high quality:
- New knowledge entries are accurate (match the implementation)
- Updated entries do not contradict existing correct documentation
- No important implementation details are omitted
- Cross-references between docs are consistent

**Checked by:** `docs-consistency-reviewer` (post-knowledge-curator run).

**Sequence:** knowledge-curator writes → docs-consistency-reviewer verifies. If docs-consistency-reviewer finds issues, knowledge-curator is re-dispatched (not the implementer).

---

## Validation Priority Order

When findings from multiple categories conflict or require prioritization:

1. Security / Data Leakage (category 9) — highest priority; PII in telemetry is an immediate blocker
2. Service Contract Compatibility (category 7) — breaking proto changes block all services
3. Observability (category 8) — incorrect telemetry defeats the purpose of the demo
4. Technical Correctness (category 5) — correctness over style
5. Distributed Flow (category 6)
6. Service Architecture (category 2) and Project Rules (category 3)
7. Domain Behavior (category 4)
8. Testing / Verification Evidence (category 11)
9. Code Quality (category 1) — style issues are lowest priority
10. Frontend / UI-Kit Consistency (category 10) — applies only to frontend changes
11. Documentation Consistency (category 12)
12. Knowledge Update Quality (category 13) — applies after code review is complete
