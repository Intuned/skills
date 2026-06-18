#!/bin/bash
# CLI hook: cleans up .intuned-agent/tab_* folders on browser stop or tab close.
# This is an intuned CLI hook (not a Claude Code hook). Receives event JSON via stdin.

INPUT=$(cat)

TRIGGER=$(echo "$INPUT" | jq -r '.trigger')
EXIT_CODE=$(echo "$INPUT" | jq -r '.payload.exitCode // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd')

# Only act on successful command completions
if [ "$TRIGGER" != "onCommandComplete" ] || [ "$EXIT_CODE" != "0" ]; then
  exit 0
fi

ARGS_STR=$(echo "$INPUT" | jq -r '.args | join(" ")')
AGENT_DIR="$CWD/.intuned-agent"

# dev browser stop / dev stealth enable|disable / dev captcha-solve enable|disable → remove all tab_* folders
if echo "$ARGS_STR" | grep -qE "^dev browser stop|^dev stealth (enable|disable)|^dev captcha-solve (enable|disable)"; then
  if [ -d "$AGENT_DIR" ]; then
    for dir in "$AGENT_DIR"/tab_*; do
      [ -d "$dir" ] && rm -rf "$dir"
    done
  fi
  exit 0
fi

# dev browser tabs close <tab_id> [tab_id2 ...] → remove each tab's folder
if echo "$ARGS_STR" | grep -q "^dev browser tabs close"; then
  # Collect all args after "close", stopping at any flag (--*)
  TAB_IDS=$(echo "$INPUT" | jq -r '
    .args as $a |
    ($a | to_entries[] | select(.value == "close") | .key) as $idx |
    [$a[($idx + 1):][] | select(startswith("--") | not)] |
    .[]
  ')

  while IFS= read -r TAB_ID; do
    if [ -n "$TAB_ID" ]; then
      TAB_DIR="$AGENT_DIR/tab_$TAB_ID"
      [ -d "$TAB_DIR" ] && rm -rf "$TAB_DIR"
    fi
  done <<< "$TAB_IDS"
  exit 0
fi
