#!/bin/bash
# SessionEnd hook: auto-save session snapshot + memory harvesting reminder
# Fires when session closes. stdout → Claude's context window.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
SESSIONS_DIR="$PROJECT_DIR/tasks/sessions"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_FILE="$SESSIONS_DIR/session-${TIMESTAMP}.md"
LATEST_RUNNER=$(find "$PROJECT_DIR/tasks/runner" -name "*.md" -type f 2>/dev/null | sort -r | head -1)

mkdir -p "$SESSIONS_DIR" || { echo "[SessionEnd] ERROR: Cannot create $SESSIONS_DIR"; exit 0; }

# Auto-generate session snapshot
{
  echo "# Session Snapshot — $TIMESTAMP"
  echo ""
  echo "## Changes This Session"
  if [ -d "$PROJECT_DIR/.git" ]; then
    # Show commits from today
    git -C "$PROJECT_DIR" log --oneline --since="8 hours ago" 2>/dev/null | sed 's/^/- /'
  fi
  echo ""
  echo "## Modified Files"
  if [ -d "$PROJECT_DIR/.git" ]; then
    STATUS_LINES=$(git -C "$PROJECT_DIR" status --short --untracked-files=all 2>/dev/null | head -20)
    if [ -n "$STATUS_LINES" ]; then
      printf '%s\n' "$STATUS_LINES" | sed 's/^/- /'
    else
      git -C "$PROJECT_DIR" diff --name-only HEAD~5 HEAD 2>/dev/null | sed 's/^/- /' | head -20
    fi
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
  echo "## TODO (agent fills before exit)"
  echo "- What Worked:"
  echo "- What Did NOT Work:"
  echo "- Decisions Made:"
  echo "- Next Step:"
  echo "- Memory Harvest: (new insights to save to docs/)"
} > "$SNAPSHOT_FILE"

# ADR-55: native-memory reconcile→render (no-op if MIR_NATIVE_MEMORY_HOME unset)
if [ -n "${MIR_NATIVE_MEMORY_HOME:-}" ] && [ -d "$MIR_NATIVE_MEMORY_HOME" ]; then
  if cd "$PROJECT_DIR" && uv run python -c "from mir.core.engine.memory import distill" 2>/dev/null; then
    _NM_DB="$PROJECT_DIR/.mir/memory.db"
    _NM_TAX="$PROJECT_DIR/config/native-memory-taxonomy.json"
    if [ -f "$_NM_DB" ] && [ -f "$_NM_TAX" ]; then
      cd "$PROJECT_DIR" && uv run python - <<'PYEOF' 2>/dev/null || true
import os, sys, pathlib
project = pathlib.Path(os.environ["CLAUDE_PROJECT_DIR"])
home = pathlib.Path(os.environ["MIR_NATIVE_MEMORY_HOME"])
from mir.core.engine.memory import distill, store
conn_obj = store.connect(project / ".mir" / "memory.db", load_vec=False)
conn = conn_obj.conn
try:
    summary = distill.session_end_reconcile_and_render(
        conn,
        source_dir=home,
        output_dir=home,
        taxonomy_path=project / "config" / "native-memory-taxonomy.json",
    )
    conn.commit()
    print(f"[ADR-55] native-memory: ingested={summary.ingested_count} tombstoned={summary.tombstoned_count} quarantine={summary.quarantine_count}")
finally:
    conn.close()
PYEOF
    fi
  fi
fi

echo "[SessionEnd] Session snapshot saved: $SNAPSHOT_FILE"
echo ""
echo "Before exiting, complete these steps:"
echo ""
echo "  1. Fill the TODO section in $SNAPSHOT_FILE"
echo ""
echo "  2. INSTINCT HARVEST — scan this session for reusable patterns:"
echo "     - Errors resolved → how? (add to lessons.md if novel)"
echo "     - User corrections → what was wrong, what's the rule? (feedback memory)"
echo "     - Workarounds discovered → framework/library quirk worth recording?"
echo "     - Conventions established → naming, structure, or flow decisions?"
echo "     - Approaches confirmed → non-obvious choice that worked (save as positive signal)"
echo "     Skip trivial patterns (typos, one-off fixes). Only save if it would help a future session."
echo "     If pattern already exists in lessons.md, increment its count instead of duplicating."
echo ""
echo "  3. Save harvested insights: docs/{category}/ + update memory-map.md"
echo "  4. Clean up older snapshots in tasks/sessions/ (keep only latest)"
