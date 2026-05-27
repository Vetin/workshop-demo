#!/usr/bin/env bash
# Installs or updates codex reviewer profiles in ~/.codex/config.toml.
# Adjusts model_instructions_file paths to the actual repo location.
#
# Usage: .codex/setup.sh [repo-root]
#   repo-root defaults to the directory containing this script.

set -euo pipefail

REPO_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
GLOBAL_CONFIG="$HOME/.codex/config.toml"
TEMPLATE="$REPO_ROOT/.codex/config.toml"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "ERROR: $TEMPLATE not found"
  exit 1
fi

# Substitute the repo root into the template
PROFILES=$(sed "s|/Users/egormasnankin/work/ai-workshop/opentelemetry-demo|$REPO_ROOT|g" "$TEMPLATE")

# Remove existing profile blocks (lines from [profiles.codex-review-*] to the next blank+[ or EOF)
# Then append fresh ones
TMPFILE=$(mktemp)

# Strip old codex-review-* profile blocks from global config
awk '
  /^\[profiles\.codex-review-(architecture|feasibility|design-generalist|structure|correctness|impl-generalist)\]/ {
    skip = 1; next
  }
  skip && /^\[/ { skip = 0 }
  skip { next }
  { print }
' "$GLOBAL_CONFIG" > "$TMPFILE"

# Append updated profiles (skip the comment header lines)
echo "" >> "$TMPFILE"
grep -v '^#' <<< "$PROFILES" >> "$TMPFILE"

mv "$TMPFILE" "$GLOBAL_CONFIG"
echo "✅ Codex reviewer profiles updated in $GLOBAL_CONFIG"
echo "   Prompt files loaded from: $REPO_ROOT/.claude/skills/*-subagent/"
