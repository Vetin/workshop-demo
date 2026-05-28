# Workshop Guide: SDD with Claude Code on OpenTelemetry Demo

This repo is a fork of the [OpenTelemetry Demo](https://opentelemetry.io/docs/demo/) — a
polyglot distributed system used as a teaching canvas. During the workshop we wired it up
with a full **Spec-Driven Development (SDD)** pipeline powered by Claude Code, then built
a real feature end-to-end through that pipeline.

Use this guide to replay the workshop at your own pace. For each step, run:

```bash
git checkout <hash>
```

...and explore what changed. The commits are ordered to tell a story.

---

## Phase 1 — Foundation

Before any AI tooling can be useful, it needs to understand the project: its rules,
its philosophy, and which external methodologies to follow. These three commits establish
that foundation.

| `git checkout` | Commit | What it does | Key concept |
|----------------|--------|--------------|-------------|
| `2eb2c6f` | chore: add third parties | Pins the ECC and Superpowers skill libraries as git submodules with locked SHAs | 📦 Skill sourcing |
| `eeed18c` | create skills from upstream | Copies raw ECC + Superpowers methodology skills into `.claude/skills/` | 🧠 Methodology |
| `288d82e` | add basic claude.md | Adds `CLAUDE.md` — project philosophy, contribution rules, and pointers to docs | 📜 Project rules |

---

## Phase 2 — Claude Code Harness

With the rules in place, we build the agent fleet and the pipeline that drives them.
This is the core of the SDD setup — an orchestrator, 50+ domain-specific agents
auto-generated from the service inventory, and the full set of SDD workflow skills.

| `git checkout` | Commit | What it does | Key concept |
|----------------|--------|--------------|-------------|
| `8cd3419` | add orchestrator agent | Adds the `sdd-orchestrator` agent and `settings.json` — the brain that routes all work through the SDD workflow | 🎯 Orchestration |
| `51abd49` | generate documentation and agents | Auto-generates 50+ agents (domain experts, implementers, reviewers) from the service inventory and bootstraps `docs/ai-knowledge/` | 🤖 Agent fleet |
| `c1e4491` | implement custom sdd skills | Implements the full SDD pipeline skills: `sdd-start`, `sdd-plan`, `sdd-execute`, `sdd-verify`, `sdd-finalize`, plus review skills and evidence templates | 🔁 SDD pipeline |

---

## Phase 3 — Advanced Pipeline

Two quality gates that make the pipeline more rigorous: automated browser verification
so UI changes are visually confirmed, and a Codex review council that debates design
and implementation plans before code is written.

| `git checkout` | Commit | What it does | Key concept |
|----------------|--------|--------------|-------------|
| `c8c9adf` | setup browser automation | Adds `browser-manual-verifier` agent, `e2e-test-author`, `e2e-test-reviewer`, and the `agent-browser` skill for visual verification | 🌐 Browser gates |
| `470f9a8` | add codex review skills | Adds the `codex-reviewer` agent and `design-plan-codex-review` / `impl-plan-codex-review` skills — a cooperative disagreement council powered by Codex | 🔍 Codex review |

---

## Phase 4 — Feature End-to-End

Now we run the complete SDD loop on a real feature: **gift-wrap option at checkout**.
These four commits show exactly what a single delivery iteration looks like — from
blank page to finalized documentation.

| `git checkout` | Commit | What it does | Key concept |
|----------------|--------|--------------|-------------|
| `4a5985c` | feat: add design doc | Brainstorming → design doc written to `docs/features/checkout-flow/changes/gift-wrap-checkout/01-design.md` | 📝 Design |
| `c0f926a` | feat: design review | Codex council reviews the design; spec updated with findings and approval in `02-design-review.md` | ✅ Review |
| `591666e` | implement | Implementation plan written (`03-implementation-plan.md`), tasks executed by implementer subagents, evidence captured in `.sdd/evidence/` | ⚙️ Execute |
| `ae4e1d0` | finalize | Final report, feature docs, AI knowledge base updated to reflect new behavior | 📦 Finalize |

---

## What You Saw

- **SDD in one sentence:** specify before you build, review before you ship, document after you land.
- **The agent fleet does the work** — the orchestrator routes, domain experts advise, implementers write code, reviewers approve.
- **Evidence is non-negotiable** — nothing is "done" without a file in `.sdd/evidence/` proving it.

### Go deeper

The full artifact trail for the gift-wrap feature lives in:

```
docs/features/checkout-flow/changes/gift-wrap-checkout/
├── 01-design.md
├── 02-design-review.md
├── 03-implementation-plan.md
├── 04-plan-review.md
└── final-report.md
```
