#!/bin/bash
# PreCompact hook: auto-save handoff + remind before compaction
# stdout → Claude's context window

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
HANDOFF_DIR="$PROJECT_DIR/tasks/handoffs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
HANDOFF_FILE="$HANDOFF_DIR/auto-${TIMESTAMP}.md"
LATEST_RUNNER=$(find "$PROJECT_DIR/tasks/runner" -name "*.md" -type f 2>/dev/null | sort -r | head -1)

mkdir -p "$HANDOFF_DIR" || { echo "[PreCompact] ERROR: Cannot create $HANDOFF_DIR"; exit 0; }

# Auto-generate handoff skeleton from current state
{
  echo "# Auto Handoff — $TIMESTAMP"
  echo ""
  echo "## Current State"
  if [ -f "$PROJECT_DIR/tasks/plan.md" ]; then
    echo '```'
    head -20 "$PROJECT_DIR/tasks/plan.md"
    echo '```'
  fi
  echo ""
  echo "## Recent Changes"
  if [ -d "$PROJECT_DIR/.git" ]; then
    git -C "$PROJECT_DIR" log --oneline -5 2>/dev/null | sed 's/^/- /'
  fi
  echo ""
  echo "## Runner State"
  if [ -n "$LATEST_RUNNER" ] && [ -f "$LATEST_RUNNER" ]; then
    echo "- Ledger: $LATEST_RUNNER"
    grep -E '^- (stage|status|last_checked_at|resume_command):' "$LATEST_RUNNER" 2>/dev/null
  else
    echo "- No runner ledger found."
  fi
  echo ""
  echo "## TODO (fill before compact)"
  echo "- Decisions:"
  echo "- Rejected alternatives:"
  echo "- Remaining risks:"
  echo "- Next actions:"
  echo "- Key files modified:"
  echo "- Runner ledger path:"
  echo "- Runner health / next inspection:"
} > "$HANDOFF_FILE"

if [ -f "$HANDOFF_FILE" ]; then
  echo "[PreCompact] Auto-handoff saved: $HANDOFF_FILE"
else
  echo "[PreCompact] ERROR: Failed to write handoff file."
fi
echo "Review and fill the TODO section before compaction proceeds."
