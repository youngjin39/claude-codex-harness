#!/bin/bash
# Codex session bootstrap stub.
#
# Referenced from .claude/hooks/pre-tool-use.sh when a code-path edit
# (tools/**, src/**, lib/**) is attempted by Claude directly. The hook
# blocks the edit and points the user here.
#
# This template ships a stub. A real implementation would:
#   - Look up the appropriate executor agent (executor-agent by default).
#   - Spawn a Codex CLI subprocess using the invocation pattern in
#     .claude/agents/executor-agent.md (perl -e 'alarm <N>; exec @ARGV'
#     codex exec ...).
#   - Capture the dispatch in tasks/log/dispatch-log.jsonl with
#     routed_via=codex_cli.
#
# For now this stub prints usage and exits 0 so a fork user understands
# what is expected without the harness erroring out on first call.
#
# Customize for your project — or replace the hook reference in
# .claude/hooks/pre-tool-use.sh with inline invocation instructions if
# your fleet does not centralize Codex session bootstrap in a script.

cat <<'USAGE'
spawn_codex_session.sh — stub

The harness expects code-path edits to flow through a Codex execution
lane (see docs/decisions/adr-09.md and adr-18.md). The default pattern
documented in .claude/agents/executor-agent.md is:

  perl -e 'alarm 120; exec @ARGV' codex exec \
    --model gpt-5-codex \
    --cd "$PWD" \
    --sandbox workspace-write \
    --skip-git-repo-check \
    --json \
    < /path/to/prompt.txt

This stub does not implement the dispatch. Replace it with your own
launcher OR invoke codex exec directly. The harness will not auto-
launch Codex on your behalf.

USAGE
exit 0
