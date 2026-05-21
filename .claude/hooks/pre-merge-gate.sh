#!/bin/bash
# PreToolUse hook stub — pre-merge gate on Bash tool calls.
#
# Wired in .claude/settings.json under PreToolUse for Bash. Default is
# no-op exit 0 so the harness boots clean on a fresh fork. Extend for
# your project (e.g. block `git merge` without a passing test suite,
# require a clean working tree before `git push`, gate `gh pr merge`
# behind a checklist).
#
# Tool-call payload arrives on stdin as JSON. Read it with:
#   payload=$(cat)
#   tool_name=$(printf '%s' "$payload" | jq -r '.tool_name // empty')
#   command=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')
#
# Exit 0 to allow. Exit 2 to BLOCK with a message on stderr (PreToolUse
# is enforced — non-zero blocks the tool call).

exit 0
