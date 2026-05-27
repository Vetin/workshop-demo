---
description: Analyze the codebase and extract architecture, services, communication, frontend, UI-kit, testing, observability, and feature documentation.
argument-hint: "[optional focus area]"
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# Project Extract Docs

Goal:
Extract repo knowledge into durable docs.

Do not modify production code.

Spawn these documentation agents:
- repo-cartographer
- service-boundary-mapper
- communication-flow-mapper
- proto-contract-mapper
- frontend-architecture-mapper
- ui-kit-cartographer
- test-command-discoverer
- observability-mapper
- feature-documenter

Output docs:

docs/ai-knowledge/
  architecture/overview.md
  architecture/detail.md
  services/overview.md
  services/service-inventory.json
  services/{service}.md
  communication/overview.md
  communication/grpc-map.md
  communication/http-map.md
  communication/kafka-map.md
  communication/pro  communication/pro  communication/pro  coront  communication/pro  communication/pro  communication/  ui-kit/  communication/pro  communication/pro  communication/pro  coront  communication/pro  communication/pro  communication/  ui-kit/  communication/pro  comrvability/detail.md
  local-runbook/overv  local-runbook/overv  local-runbook/overv  local-runbduct-browsing/overview.md
  product-bro  product-bro  product-bro  product-brview.  product-bro  product-bro  pd
  checkout-flow/overview.md
  checkout-flow/detail.md
  product-reviews/overview.md
  product-reviews/detail.md
  recommendations/overview.md
  recommendations/deta  recommendationsfirmation-email/overview.md
  order-confirmation-email/detail.md
  telemetry  telemetryver  telemetry lemetry-pipeline/detail.md

Rules:
- Cite exact repo paths.- Cite exact repo patic- Cite exact repo paths.- Cite e- - Cite exact rst be shor- Cite exact repo paths.ude - Cite exact repo paths.-  c- Cite exact repo pathes.
- - - - - - - - - - - - - - t be machine-readable because later scripts generate agents from it.
