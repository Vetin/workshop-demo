---
description: Start SDD for a feature or bug using extracted project knowledge
  and existing feature docs.
argument-hint: '[feature or bug request]'
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# SDD Start

Input:

$ARGUMENTS

## Purpose

Turn a raw user request into a design document inside the relevant feature folder.

Do not write production code.

## Feature storage rule

Active SDD work lives under:

```text
docs/features/{feature-area}/changes/{change-slug}/
```

Stable feature docs live at:

```text
docs/features/{feature-area}/overview.md
docs/features/{feature-area}/detail.md
```

## Read first

- .sdd/pipeline.md
- .sdd/pipeline.json
- docs/features/ (all existing feature docs)
- docs/ai-knowledge/architecture/overview.md
- docs/ai-knowledge/services/overview.md
- docs/ai-knowledge/communication/overview.md
- docs/ai-knowledge/frontend/overview.md
- docs/ai-knowledge/observability/overview.md
- docs/ai-knowledge/validation/sdd-human-escalation.md

## Steps

1. Classify request type: feature | bug | refactor | docs | investigation

2. Choose feature area.
   - Match to an existing feature area if the request clearly belongs there.
   - Propose a new feature area only if the request is genuinely new territory.
   - Ask user if the feature area is ambiguous.
   - **Legacy flat files**: `docs/features/{name}.md` files are legacy. If the
     chosen feature area has only a flat file (e.g., `docs/features/checkout-flow.md`)
     and no directory (`docs/features/checkout-flow/overview.md`), create the
     directory structure and copy the flat file content into `overview.md` before
     creating the change folder. Do not delete the flat file — leave it as a
     redirect stub or for human cleanup.

3. Choose change slug (kebab-case, descriptive, no dates).
   Example: for feature area `checkout-flow`, slug: `gift-wrap-checkout`

4. Choose the change folder path:
   `docs/features/{feature-area}/changes/{change-slug}/`

5. Read the relevant stable feature docs (`overview.md`, `detail.md`) if they exist.

6. Restate the request in business/system language.

7. Identify impacted services and modules from the request.

8. Identify potential impacts:
   - contracts (proto changes, HTTP API changes),
   - service communication,
   - telemetry (new spans, metrics, logs, attribute changes),
   - tests,
   - security / sensitive data,
   - docs.

9. Ask only blocking questions (questions where the answer fundamentally changes
   the design). Convert all non-blocking uncertainty into explicit assumptions.

10. Create:
    `docs/features/{feature-area}/changes/{change-slug}/01-design.md`
    using the template at `docs/features/_template/changes/_template/01-design.md`.

11. Self-review the design for:
    - missing acceptance criteria,
    - missing edge cases,
    - unclear service boundaries,
    - hidden contract changes,
    - telemetry impact not documented,
    - missing verification path.

12. Ask user for approval before planning.

## Output

At the end, provide:

- feature area,
- change slug,
- design doc path,
- blocking questions if any,
- assumptions list,
- recommended next command:

  `/sdd-review-design {feature-area}/{change-slug}`
