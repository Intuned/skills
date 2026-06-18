#!/bin/bash
# CLI hook: outputs network tracking hint on tab/browser creation.
# This is an intuned CLI hook (not a Claude Code hook). Receives event JSON via stdin.
# Outputs JSON with __log to append text to the CLI output.

INPUT=$(cat)

TRIGGER=$(echo "$INPUT" | jq -r '.trigger')
EXIT_CODE=$(echo "$INPUT" | jq -r '.payload.exitCode // empty')

# Only act on successful command completions
if [ "$TRIGGER" != "onCommandComplete" ] || [ "$EXIT_CODE" != "0" ]; then
  exit 0
fi

ARGS_STR=$(echo "$INPUT" | jq -r '.args | join(" ")')

network_hint() {
  local TAB_ID="$1"
  cat <<EOF
Network traces for this tab will be recorded to:
  .intuned-agent/tab_${TAB_ID}/network/
    - requests.txt: [time] #id METHOD url STATUS | SIZE | CONTENT_TYPE | RESOURCE_TYPE [→ body file] [frame: URL]
    - request_bodies/: Response bodies (.body) and POST request bodies (.request)
  Note: this folder is deleted when the tab or browser is closed.
EOF
}

# dev browser start / dev stealth enable|disable / dev captcha-solve enable|disable → hint for initial tab
if echo "$ARGS_STR" | grep -qE "^dev browser start|^dev stealth (enable|disable)|^dev captcha-solve (enable|disable)"; then
  TAB_ID=$(echo "$INPUT" | jq -r '.payload.jsonOutput.initialTabId // empty')
  if [ -n "$TAB_ID" ]; then
    jq -nc --arg log "$(network_hint "$TAB_ID")" '{"__log": $log}'
  fi
  exit 0
fi

# dev browser tabs create → hint for new tab
if echo "$ARGS_STR" | grep -q "^dev browser tabs create"; then
  TAB_ID=$(echo "$INPUT" | jq -r '.payload.jsonOutput.tab.tabId // empty')
  if [ -n "$TAB_ID" ]; then
    jq -nc --arg log "$(network_hint "$TAB_ID")" '{"__log": $log}'
  fi
  exit 0
fi
