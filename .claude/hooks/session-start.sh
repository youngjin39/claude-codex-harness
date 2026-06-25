#!/bin/bash
_MIR_HOOK_TIER="warn"
_mir_session_body() {
# SessionStart hook: inject startup context into the session
# stdout → Claude's context window
# ADR-53 D1: current-only core — upfront context + plan head + intent.json + lessons head.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Auto-archive DONE/CLOSED plan.md sections before loading (silent).
# Skip in a delegated/sub-agent (codex) session: tasks/plan.md is the control-plane
# main's cursor (ADR-60 R5) and a dispatch worktree's session-start must not mutate it,
# else the archive edit contaminates the dispatch merge changeset -> denied-harness gate
# block (observed 2026-06-25: a worktree session-start archived plan.md, blocking the merge).
if [ -z "${MIR_CODEX_SESSION_ID:-}" ]; then
python3 - "$PROJECT_DIR" 2>/dev/null <<'PYEOF' || true
import re, sys, datetime
from pathlib import Path
pd = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
plan_p = pd / "tasks" / "plan.md"
if not plan_p.exists():
    sys.exit(0)
text = plan_p.read_text("utf-8")
DONE = re.compile(r"\(.*\bDONE\b.*\)")
CLOSED = re.compile(r"\(.*\bCLOSED\b.*\)")
preamble, sections, cur_h, cur_b = [], [], None, []
for line in text.splitlines(keepends=True):
    if line.startswith("## "):
        if cur_h is not None:
            sections.append((cur_h, cur_b))
        cur_h, cur_b = line[3:].rstrip(), []
    elif cur_h is None:
        preamble.append(line)
    else:
        cur_b.append(line)
if cur_h is not None:
    sections.append((cur_h, cur_b))
month = datetime.date.today().strftime("%Y-%m")
arch, keep = [], []
for h, b in sections:
    if (DONE.search(h) or CLOSED.search(h)) and "Pinned Tracker Policies" not in h:
        arch.append((h, b))
    else:
        keep.append((h, b))
if not arch:
    sys.exit(0)
arch_p = pd / "tasks" / "archive" / f"plan-archive-{month}.md"
arch_p.parent.mkdir(parents=True, exist_ok=True)
if not arch_p.exists():
    arch_p.write_text(f"# Plan Archive {month}\n\n", "utf-8")
with arch_p.open("a", encoding="utf-8") as f:
    for h, b in arch:
        f.write(f"## {h}\n{''.join(b)}\n")
plan_text = "".join(preamble) + "".join(f"## {h}\n{''.join(b)}" for h, b in keep)
plan_p.write_text(plan_text, "utf-8")
print(f"[plan-archive] archived {len(arch)} section(s)")
PYEOF
fi

echo "=== SESSION CONTEXT ==="

if [ -f "$PROJECT_DIR/scripts/build_session_upfront_context.py" ]; then
  _UPFRONT=$(python3 "$PROJECT_DIR/scripts/build_session_upfront_context.py" "$PROJECT_DIR" 2>/dev/null)
  _INTENT_CONFLICT_ADVISORY=$(printf '%s\n' "$_UPFRONT" | sed -n 's/^intent_conflict_advisory: //p' | head -n 1)
  echo "=== UPFRONT CONTEXT ==="
  echo "$_UPFRONT"
  echo "=== END UPFRONT CONTEXT ==="
  echo ""
fi

if [ -f "$PROJECT_DIR/tasks/plan.md" ]; then
  echo "--- plan.md ---"
  python3 -c "
import sys
data = open('$PROJECT_DIR/tasks/plan.md', 'rb').read(1400)
text = data[:1200].decode('utf-8', errors='ignore')
sys.stdout.write(text)
" 2>/dev/null
  echo ""
fi

if [ -f "$PROJECT_DIR/tasks/intent.json" ]; then
  _INTENT_OUT=$(python3 -c "
import json, sys
try:
    d = json.load(open('$PROJECT_DIR/tasks/intent.json'))
    for k in ('goal_type', 'scope', 'priority', 'goal', 'updated'):
        v = d.get(k, '')
        if v:
            print(f'{k}: {v}')
except Exception:
    pass
" 2>/dev/null)
  if [ -n "$_INTENT_OUT" ]; then
    echo "--- intent.json ---"
    echo "$_INTENT_OUT"
    if [ -n "$_INTENT_CONFLICT_ADVISORY" ]; then
      echo "intent_conflict_advisory: $_INTENT_CONFLICT_ADVISORY"
    fi
    echo ""
  fi
fi

echo ""

# mir:adr53:context-core:begin
# ADR-53 D1 (per-family): DB-live active lessons head + context-pull hint.
_MIR_PD="${CLAUDE_PROJECT_DIR:-${PROJECT_DIR:-.}}"
_MIR_DB="$_MIR_PD/.mir/memory.db"
if [ -f "$_MIR_DB" ]; then
  _MIR_LESSONS=$(python3 - "$_MIR_DB" 2>/dev/null <<'PYEOF'
import sys, sqlite3
db_path = sys.argv[1]
try:
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """
        SELECT e.slug, f.object_literal
          FROM facts f
          JOIN entities e ON e.id = f.subject_entity_id
         WHERE f.predicate = 'lesson'
           AND f.status    = 'active'
         ORDER BY f.id DESC
         LIMIT 15
        """
    ).fetchall()
    conn.close()
    for slug, text in rows:
        print(f"- **{slug}**: {text}")
except Exception:
    sys.exit(1)
PYEOF
)
  _DB_EXIT=$?
  if [ "$_DB_EXIT" -eq 0 ] && [ -n "$_MIR_LESSONS" ]; then
    echo ""
    echo "--- lessons (DB-live, active only) ---"
    echo "$_MIR_LESSONS"
  elif [ "$_DB_EXIT" -ne 0 ] && [ -f "$_MIR_PD/tasks/lessons.md" ]; then
    echo ""
    echo "--- lessons.md (fallback: memory.db unavailable) ---"
    head -30 "$_MIR_PD/tasks/lessons.md"
  fi
elif [ -f "$_MIR_PD/tasks/lessons.md" ]; then
  echo ""
  echo "--- lessons.md (fallback: memory.db unavailable) ---"
  head -30 "$_MIR_PD/tasks/lessons.md"
fi
echo ""
echo "Context depth on demand: uv run mir context pull \"<query>\" (--history for archived/expired)"
# mir:adr53:context-core:end

# ADR-55 doc-size advisory guard (review major docs)
if command -v uv >/dev/null 2>&1 && [ -f "$CLAUDE_PROJECT_DIR/config/doc-size-guard.json" ]; then
  _DG=$(cd "$CLAUDE_PROJECT_DIR" && uv run mir doc-guard --config config/doc-size-guard.json --project-dir "$CLAUDE_PROJECT_DIR" 2>/dev/null) || true
  [ -n "$_DG" ] && echo "$_DG"
fi

# mir:profile:enforcement:begin
# Generated by your-harness Profile Compiler (tools/profile_compiler). DO NOT EDIT MANUALLY.
# Source: .mir/repo-profile.toml — edit profile and recompile to update this block.
# Role policy reminder injected into session-start for family: your-harness
MIR_CODEX_DEFAULT_ENABLED="true"
echo "[mir] role policy active: main_agent_parity=claude_codex delegated_backend=codex_first codex_backend=code_tdd_review_plane codex_default=$MIR_CODEX_DEFAULT_ENABLED family=your-harness" >&2
if [ -n "${MIR_CODEX_SESSION_ID:-}" ]; then
    echo "[mir] active codex session: $MIR_CODEX_SESSION_ID modes=$MIR_CODEX_ALLOWED_MODES" >&2
elif [ "$MIR_CODEX_DEFAULT_ENABLED" = "true" ]; then
    echo "[mir] no active codex session — delegated backend-capable execution in code_paths will be blocked by pre-tool-use hook" >&2
fi

# mir:profile:enforcement:end

}

# Snapshot global Claude/Codex config files into a local git history repo.
# Runs silently; always exits 0; must not add to injected context bytes.
timeout 10 bash "${CLAUDE_PROJECT_DIR:-.}/scripts/backup_global_claude_config.sh" >/dev/null 2>&1 || true

# mir:f3:stdout-cap:begin
# token-efficiency F3 (2026-06-10): template-parity 10,240B stdout cap (UTF-8 safe).
_mir_session_body "$@" | python3 -c '
import sys
data = sys.stdin.buffer.read()
limit = 10240
if len(data) <= limit:
    sys.stdout.buffer.write(data)
else:
    cut = data[: limit - 64].decode("utf-8", errors="ignore")
    sys.stdout.write(cut + "\n[mir] session-start context truncated at 10KB (F3 cap)\n")
'
# mir:f3:stdout-cap:end
