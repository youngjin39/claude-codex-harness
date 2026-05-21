#!/bin/bash
# TaskCreated hook stub — TDD task-creation gate.
#
# Wired in .claude/settings.json under TaskCreated. Default is no-op
# exit 0 so the harness boots clean on a fresh fork. Extend for your
# project (e.g. require a failing test before the task can proceed, or
# block tasks that touch production code without a corresponding test
# task).
#
# Task payload arrives on stdin as JSON. Read it with:
#   payload=$(cat)
#   task_id=$(printf '%s' "$payload" | jq -r '.task.id // empty')
#   subject=$(printf '%s' "$payload" | jq -r '.task.subject // empty')
#
# Exit 0 to allow. Exit 2 to BLOCK with a message on stderr.

exit 0
