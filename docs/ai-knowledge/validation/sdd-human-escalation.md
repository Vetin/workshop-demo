# SDD Human Escalation

Ask the user only when the decision cannot be safely made from the approved design, plan, docs, or code.

## Ask user when

- product behavior is unclear,
- feature area is ambiguous,
- service boundary changes,
- public contract changes,
- telemetry semantics change,
- sensitive data handling changes,
- rollout strategy changes,
- feature scope changes,
- reviewers disagree on architecture/security/product issue,
- plan is wrong,
- repeated verification failure has no new information.

## Do not ask user when

- the next task is clear,
- a reviewer finding is fixable without changing intent,
- tests fail for an obvious implementation reason,
- docs need routine updates,
- implementer needs code context the orchestrator can provide,
- a mechanical refactor is required by the accepted plan.

## Question format

When asking the user:

1. State the blocker.
2. Show the options.
3. Recommend one option.
4. Explain consequences.
5. Ask for one decision.
