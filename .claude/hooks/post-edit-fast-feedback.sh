#!/usr/bin/env bash
# post-edit-fast-feedback.sh — PostToolUse(Edit|Write) hook
#
# Records changed files to .sdd/evidence/changed-files.txt for
# downstream gate and review-router hooks.
# Does NOT run gates here — that happens at subagent stop.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
EVIDENCE_DIR="$REPO_ROOT/.sdd/evidence"
mkdir -p "$EVIDENCE_DIR"

# Read JSON payload from stdin
PAYLOAD="$(cat)"

# Extract file_path from the JSON (Edit tool) or file_path (Write tool)
FILE_PATH="$(echo "$PAYLOAD" | python3 -c "
import json, sys
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
# Edit has file_path, Write has file_path
print(inp.get('file_path', ''))
" 2>/dev/null || true)"

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Make path relative to repo root
REL_PATH="${FILE_PATH#$REPO_ROOT/}"

# Append to changed-files list (dedup)
CHANGED_FILE="$EVIDENCE_DIR/changed-files.txt"
touch "$CHANGED_FILE"
if ! grep -qxF "$REL_PATH" "$CHANGED_FILE" 2>/dev/null; then
  echo "$REL_PATH" >> "$CHANGED_FILE"
fi

# Fast feedback: warn if editing generated files
case "$REL_PATH" in
  src/*/genproto/*|src/recommendation/demo_pb2*|src/product-reviews/demo_pb2*|src/frontend/protos/demo.ts)
    echo "⚠️  WARNING: Editing generated file $REL_PATH" >&2
    echo "   Run 'make docker-generate-protobuf' instead of editing generated files directly." >&2
    ;;
  pb/demo.proto)
    echo "ℹ️  NOTE: pb/demo.proto changed — remember to run 'make docker-generate-protobuf'" >&2
    echo "   and update all generated stubs in genproto/, demo_pb2*.py, demo.ts" >&2
    ;;
esac

exit 0
