# Design: Workshop Step-by-Step Guide

**Date:** 2026-05-28  
**Topic:** WORKSHOP.md — async learner guide for the SDD workshop branch  
**Status:** Approved

## Goal

A single `WORKSHOP.md` at the repo root that lets spectators replay the workshop at their own pace by stepping through git commits. High-level summary only — scannable in under 10 minutes.

## Audience

Async learners who were not at the live session. They clone or fork the repo and follow the guide independently.

## Format

Grouped phases (Option B). Each phase has:
- A short paragraph explaining the concept
- A mini-table: `git checkout <hash>` | commit name | 1-sentence description | key concept badge

## Structure

### Intro (3 sentences)
What this repo is, what SDD + Claude Code means, how to use the guide.

### Phase 1 — Foundation (3 commits: 2eb2c6f, eeed18c, 288d82e)
Third-party skill references, ECC/superpowers skills, CLAUDE.md.  
Concept: *how Claude learns a project's rules and methodology*

### Phase 2 — Claude Code Harness (3 commits: 8cd3419, 51abd49, c1e4491)
SDD orchestrator agent, 50+ domain agents, full SDD pipeline skills.  
Concept: *the agent fleet and the workflow that drives them*

### Phase 3 — Advanced Pipeline (2 commits: c8c9adf, 470f9a8)
Browser automation verifier, Codex review council.  
Concept: *quality gates that run automatically before code ships*

### Phase 4 — Feature End-to-End (4 commits: 4a5985c, c0f926a, 591666e, ae4e1d0)
Gift-wrap checkout: design → review → implement → finalize.  
Concept: *the complete SDD workflow in practice*

### Closing (3 bullets + deep-read link)
What you saw summary. Link to `docs/features/checkout-flow/changes/gift-wrap-checkout/`.

## Constraints

- No code snippets — summary only
- No implementation detail within WORKSHOP.md itself
- Use real commit hashes from the workshop branch
