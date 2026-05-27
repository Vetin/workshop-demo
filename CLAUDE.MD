# CLAUDE.md

This fork is used for an AI workshop on Spec-Driven Development.

## Project philosophy

OpenTelemetry Demo is a distributed systems teaching app. Preserve that spirit.

Prefer changes that are:

- small,
- observable,
- well-documented,
- easy to verify,
- consistent with existing service boundaries.

## Contribution rules for this fork

- Do not add new services unless the user explicitly approves it.
- Do not hide telemetry-impacting changes.
- Do not claim completion without local verification evidence.
- Do not modify generated files unless the generator path is documented.
- Keep project knowledge in docs/ai-knowledge.
- Keep feature behavior in docs/features.
- Keep active SDD work in docs/features/.

The detailed SDD workflow is owned by the default sdd-orchestrator agent, not by this file.
