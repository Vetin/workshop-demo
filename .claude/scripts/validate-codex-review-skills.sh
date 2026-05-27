#!/usr/bin/env bash
# validate-codex-review-skills.sh
#
# Smoke-tests the Codex review skills against demo plans via `claude -p`.
# Each test runs preflight + round 1 spawn only — does NOT run the full council loop.
#
# Usage:
#   .claude/scripts/validate-codex-review-skills.sh [design|impl|both]
#
# Default: both

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DESIGN_PLAN="${1:-/tmp/demo-design-plan.md}"
IMPL_PLAN="${2:-/tmp/demo-impl-plan.md}"
TARGET="${3:-both}"

# Override: if first arg is design/impl/both, shift and use defaults for plans
if [[ "${1:-}" == "design" || "${1:-}" == "impl" || "${1:-}" == "both" ]]; then
  TARGET="${1}"
  DESIGN_PLAN="/tmp/demo-design-plan.md"
  IMPL_PLAN="/tmp/demo-impl-plan.md"
fi

PASS=0
FAIL=0

banner() { echo ""; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; echo "  $*"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; }

run_test() {
  local label="$1"
  local skill="$2"
  local plan="$3"

  banner "TEST: $label"
  echo "  Skill : $skill"
  echo "  Plan  : $plan"
  echo ""

  if [[ ! -f "$plan" ]]; then
    echo "SKIP — plan file not found: $plan"
    return
  fi

  local prompt="Use the skill ${skill} for the plan at ${plan}.

Run only the preflight check and round 1 (spawn both reviewers, collect their initial responses).

After both codex-reviewer agents return their responses, report:
1. Whether preflight passed (yes/no and why if no)
2. The THREAD_ID returned by each reviewer
3. The first 300 characters of each review
4. Whether watchdogKilled was true for either reviewer

Then STOP — do not triage findings, do not run the council loop, do not resume reviewers."

  local output
  local exit_code=0

  output=$(cd "$PROJECT_DIR" && claude --dangerously-skip-permissions -p "$prompt" 2>&1) || exit_code=$?

  echo "$output"
  echo ""

  if echo "$output" | grep -qi "THREAD_ID:"; then
    echo "✅ PASS — THREAD_ID found in output (Codex spawn worked)"
    PASS=$((PASS + 1))
  elif echo "$output" | grep -qi "preflight.*fail\|MISSING\|not found\|error"; then
    echo "⚠️  PREFLIGHT FAILED — environment issue, not a skill bug"
    FAIL=$((FAIL + 1))
  else
    echo "❌ FAIL — no THREAD_ID in output and no clear preflight error"
    FAIL=$((FAIL + 1))
  fi
}

# ── Design plan skill ──────────────────────────────────────────────────────
if [[ "$TARGET" == "design" || "$TARGET" == "both" ]]; then
  run_test \
    "design-plan-codex-review-subagent" \
    "design-plan-codex-review-subagent" \
    "$DESIGN_PLAN"
fi

# ── Impl plan skill ────────────────────────────────────────────────────────
if [[ "$TARGET" == "impl" || "$TARGET" == "both" ]]; then
  run_test \
    "impl-plan-codex-review-subagent" \
    "impl-plan-codex-review-subagent" \
    "$IMPL_PLAN"
fi

# ── Summary ────────────────────────────────────────────────────────────────
banner "SUMMARY"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo ""
if [[ $FAIL -eq 0 ]]; then
  echo "All tests passed ✅"
  exit 0
else
  echo "Some tests failed ❌"
  exit 1
fi
