#!/bin/bash
# SessionStart hook (Claude Code): materialize the Intuned agent CLI hooks into
# this project's .intuned/ so they are active out of the box for the session.
#
# Runs `intuned dev agent-hooks setup`, which writes .intuned/hooks.json and
# the hook scripts under .intuned/agent-hooks/. Failure is non-fatal — the agent
# can still work; some CLI ergonomics (artifact capture, result compaction,
# proactive browser connect) just won't be active.

INPUT=$(cat)

# Resolve the project directory from the hook input; fall back to PWD.
CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
[ -z "$CWD" ] && CWD="$PWD"

( cd "$CWD" && intuned dev agent-hooks setup >/dev/null 2>&1 ) || true

exit 0
