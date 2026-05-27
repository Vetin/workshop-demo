#!/usr/bin/env bash
# gate-router.sh — Choose and run the appropriate quality gate level
# based on which files have changed.
#
# Usage:
#   gate-router.sh [--level fast|medium|full] [changed_file ...]
#   If --level is omitted, the level is inferred from changed files.
#   If no files are provided, git status is used.
#
# Exit codes:
#   0 = all gates passed
#   1 = gate failed (output contains details)
#   2 = configuration error

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# ── Level inference ────────────────────────────────────────────────────────────

infer_level() {
  local files=("$@")
  local has_proto=false
  local has_source=false
  local has_docker=false
  local has_docs_only=true

  for f in "${files[@]}"; do
    case "$f" in
      *.proto)             has_proto=true; has_docs_only=false ;;
      Dockerfile*|*.dockerfile) has_docker=true; has_docs_only=false ;;
      src/*/*)
        has_source=true; has_docs_only=false ;;
      docker-compose*.yml|kubernetes/*|.env*)
        has_docker=true; has_docs_only=false ;;
      docs/*|specs/*|*.md)
        : ;;  # docs only
      *)
        has_docs_only=false ;;
    esac
  done

  if $has_proto; then
    echo "medium"
  elif $has_source || $has_docker; then
    echo "medium"
  elif $has_docs_only; then
    echo "fast"
  else
    echo "fast"
  fi
}

# ── Gate runners ───────────────────────────────────────────────────────────────

run_fast_gate() {
  echo "▶ Running FAST gate (spell, markdown, YAML, license, links)…"
  local failed=()

  make misspell 2>&1 || failed+=("misspell")
  make markdownlint 2>&1 || failed+=("markdownlint")
  make yamllint 2>&1 || failed+=("yamllint")
  make checklicense 2>&1 || failed+=("checklicense")

  if [[ ${#failed[@]} -gt 0 ]]; then
    echo "FAST gate FAILED: ${failed[*]}" >&2
    return 1
  fi
  echo "✓ FAST gate passed."
}

run_medium_gate() {
  echo "▶ Running MEDIUM gate (fast + proto generation + build)…"
  run_fast_gate || return 1

  if [[ "${SKIP_BUILD:-}" != "1" ]]; then
    make docker-generate-protobuf 2>&1 || { echo "MEDIUM gate FAILED: docker-generate-protobuf" >&2; return 1; }
    make check-clean-work-tree 2>&1   || { echo "MEDIUM gate FAILED: check-clean-work-tree" >&2; return 1; }
  else
    echo "  (skipping Docker build — SKIP_BUILD=1)"
  fi
  echo "✓ MEDIUM gate passed."
}

run_full_gate() {
  echo "▶ Running FULL gate (medium + stack + trace tests + frontend tests)…"
  run_medium_gate || return 1
  make start 2>&1               || { echo "FULL gate FAILED: make start" >&2; return 1; }
  make run-tracetesting 2>&1    || { echo "FULL gate FAILED: run-tracetesting" >&2; return 1; }
  make run-tests 2>&1           || { echo "FULL gate FAILED: run-tests" >&2; return 1; }
  make stop 2>&1 || true
  echo "✓ FULL gate passed."
}

# ── Main ───────────────────────────────────────────────────────────────────────

LEVEL=""
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --level)
      LEVEL="$2"; shift 2 ;;
    *)
      CHANGED_FILES+=("$1"); shift ;;
  esac
done

# If no files supplied, collect from git
if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  mapfile -t CHANGED_FILES < <(git diff --name-only HEAD 2>/dev/null; git diff --name-only --cached 2>/dev/null)
fi

# Infer level if not specified
if [[ -z "$LEVEL" ]]; then
  LEVEL="$(infer_level "${CHANGED_FILES[@]:-}")"
fi

echo "Gate level: $LEVEL"
echo "Changed files: ${CHANGED_FILES[*]:-<none detected>}"

case "$LEVEL" in
  fast)   run_fast_gate ;;
  medium) run_medium_gate ;;
  full)   run_full_gate ;;
  *)
    echo "Unknown gate level: $LEVEL (expected fast|medium|full)" >&2
    exit 2
    ;;
esac
