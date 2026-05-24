#!/bin/bash
# TaskCreated enforcement gate: deny task creation when tasks/tdd.json has no active ledger entry.
# P0-I active enforcement: fail-closed on python3 parse error or empty output (BUG C1 fix).
# Multi-schema support (P1-quality): accepts 'changes', 'history', 'entries',
# root-level 'categories', and root-level 'targets'.

set -u

TDD_JSON="${CLAUDE_PROJECT_DIR:-.}/tasks/tdd.json"

if [ ! -f "$TDD_JSON" ]; then
  echo "[tdd-task-created] no tdd.json — task creation requires composite TDD ledger" >&2
  exit 2
fi

if ! RESULT=$(python3 -c "
import json, sys

data = json.load(open('$TDD_JSON'))

# Try each known list-type entry key in priority order.
for key in ('changes', 'history', 'entries'):
    val = data.get(key)
    if isinstance(val, list):
        sys.stdout.write('LIST:' + str(len(val)))
        sys.exit(0)

# Flat root-level categories: treat as an active composite ledger.
root_categories = data.get('categories')
if isinstance(root_categories, dict):
    sys.stdout.write('ROOT_CATEGORIES')
    sys.exit(0)

# Flat root-level targets: allow only when there is at least one declared target.
root_targets = data.get('targets')
if isinstance(root_targets, list):
    sys.stdout.write('TARGETS:' + str(len(root_targets)))
    sys.exit(0)

sys.stdout.write('UNKNOWN_SCHEMA')
" 2>/dev/null); then
  echo "[tdd-task-created] tdd.json parse error — task creation blocked" >&2
  exit 2
fi

if [ -z "$RESULT" ]; then
  echo "[tdd-task-created] tdd.json parse returned empty — task creation blocked" >&2
  exit 2
fi

# Legacy flat-object schema with no recognizable TDD shape — allow.
if [ "$RESULT" = "UNKNOWN_SCHEMA" ]; then
  exit 0
fi

if [ "$RESULT" = "ROOT_CATEGORIES" ]; then
  exit 0
fi

if [ "${RESULT#TARGETS:}" != "$RESULT" ]; then
  TARGETS_COUNT="${RESULT#TARGETS:}"
  if [ "$TARGETS_COUNT" = "0" ]; then
    echo "[tdd-task-created] tdd.json has no targets — task creation requires active ledger" >&2
    exit 2
  fi
  exit 0
fi

# LIST:<count> — extract count
CHANGES_COUNT="${RESULT#LIST:}"

if [ "$CHANGES_COUNT" = "0" ]; then
  echo "[tdd-task-created] tdd.json has no entries — task creation requires active ledger" >&2
  exit 2
fi

exit 0
