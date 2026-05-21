#!/bin/bash
# PostToolUse hook stub — post-edit self-ingest.
#
# Wired in .claude/settings.json under PostToolUse for Bash | apply_patch
# | Edit | Write. Default is no-op exit 0 so the harness boots clean on a
# fresh fork. Extend for your project (e.g. update a search index, log
# the edited file to a journal, trigger a doc lint).
#
# Tool-call payload arrives on stdin as JSON. Read it with:
#   payload=$(cat)
#   tool_name=$(printf '%s' "$payload" | jq -r '.tool_name // empty')
#   file_path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')
#
# Exit 0 to allow the tool to continue. Non-zero exits do NOT block the
# tool call (PostToolUse fires AFTER the edit) but are reported in the
# session transcript.

exit 0
