#!/bin/bash
# TaskCompleted hook stub — TDD task-completion gate.
#
# Wired in .claude/settings.json under TaskCompleted. Default is no-op
# exit 0 so the harness boots clean on a fresh fork. Extend for your
# project (e.g. require a green test run for the linked test file, or
# block completion when the related test was never updated).
#
# Task payload arrives on stdin as JSON. Read it with:
#   payload=$(cat)
#   task_id=$(printf '%s' "$payload" | jq -r '.task.id // empty')
#   subject=$(printf '%s' "$payload" | jq -r '.task.subject // empty')
#
# Exit 0 to allow. Exit 2 to BLOCK with a message on stderr.

exit 0
