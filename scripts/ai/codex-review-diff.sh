#!/usr/bin/env bash
# codex-review-diff.sh — Run Codex-based diff review on changed files.
#
# Requires: @openai/codex CLI available as `codex`
#
# Usage:
#   codex-review-diff.sh [--reviewer code-changes|structure|correctness] [file1 file2 ...]
#
# Exit codes:
#   0 = review passed or codex not available
#   1 = review found blockers
#   2 = usage error

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
EVIDENCE_DIR="$REPO_ROOT/.sdd/evidence"
mkdir -p "$EVIDENCE_DIR"

REVIEWER="${REVIEWER:-code-changes}"
FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reviewer) REVIEWER="$2"; shift 2 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

# Check codex availability
if ! command -v codex &>/dev/null; then
  echo "codex CLI not found — skipping Codex review (install @openai/codex to enable)"
  exit 0
fi

# Get diff
if [[ ${#FILES[@]} -gt 0 ]]; then
  DIFF="$(git diff HEAD -- "${FILES[@]}" 2>/dev/null || true)"
else
  DIFF="$(git diff HEAD 2>/dev/null || true)"
fi

if [[ -z "$DIFF" ]]; then
  echo "No diff to review."
  exit 0
fi

DIFF_FILE="$(mktemp /tmp/otel-demo-diff-XXXXXX.patch)"
echo "$DIFF" > "$DIFF_FILE"

echo "▶ Running Codex $REVIEWER review…"

PROMPT="You are a $REVIEWER reviewer for the OpenTelemetry Demo workshop fork.

Review the following git diff. Focus on:
- Correctness of OpenTelemetry instrumentation
- Service boundary violations
- Security issues (PII in spans, unsafe flag behavior)
- Breaking changes to proto contracts
- Missing or broken tests

Diff:
\`\`\`diff
$(cat "$DIFF_FILE")
\`\`\`

Respond with:
1. PASS or BLOCK
2. If BLOCK: bullet list of specific issues with file:line references
3. If PASS: one-line summary of what looks good"

REVIEW_OUTPUT="$(echo "$PROMPT" | codex --model o4-mini 2>&1 || echo "CODEX_ERROR")"

rm -f "$DIFF_FILE"

if [[ "$REVIEW_OUTPUT" == "CODEX_ERROR" ]]; then
  echo "Codex review error — skipping" >&2
  exit 0
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REVIEW_FILE="$EVIDENCE_DIR/codex-review-$REVIEWER-$TIMESTAMP.md"
cat > "$REVIEW_FILE" <<EOF
# Codex Review: $REVIEWER
Timestamp: $TIMESTAMP
Reviewer: $REVIEWER

## Output
$REVIEW_OUTPUT
EOF

echo "Review written → $REVIEW_FILE"
echo "$REVIEW_OUTPUT"

# Block if BLOCK found
if echo "$REVIEW_OUTPUT" | grep -qi "^BLOCK"; then
  echo "" >&2
  echo "🚫 Codex review BLOCKED — fix the issues above before proceeding." >&2
  exit 1
fi

exit 0
