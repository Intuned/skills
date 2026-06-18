#!/bin/bash
# intuned CLI hook: notifies the MCP control server to proactively connect to the browser.
# Triggers on browser start and tab creation so network tracking begins immediately,
# without waiting for the first MCP tool call on a tab.
#
# This is an intuned CLI hook (not a Claude Code hook). Receives event JSON via stdin.

INPUT=$(cat)

TRIGGER=$(echo "$INPUT" | jq -r '.trigger')
EXIT_CODE=$(echo "$INPUT" | jq -r '.payload.exitCode // empty')

# Only act on successful command completions
if [ "$TRIGGER" != "onCommandComplete" ] || [ "$EXIT_CODE" != "0" ]; then
  exit 0
fi

ARGS_STR=$(echo "$INPUT" | jq -r '.args | join(" ")')

# Act on: browser start, stealth/captcha toggles (which restart the browser), and tab creation
if ! echo "$ARGS_STR" | grep -qE "^dev browser start|^dev stealth (enable|disable)|^dev captcha-solve (enable|disable)|^dev browser tabs create"; then
  exit 0
fi

# Use CLAUDE_SDK_WORKING_DIRECTORY (static project root) to avoid breakage when
# the agent has run `cd` and changed its working directory.
CWD="${CLAUDE_SDK_WORKING_DIRECTORY:-$(echo "$INPUT" | jq -r '.cwd')}"

# Find the MCP control server port
CONTROL_PORT_FILE="$CWD/.intuned/mcp-control-port"
if [ ! -f "$CONTROL_PORT_FILE" ]; then
  exit 0
fi

PORT=$(cat "$CONTROL_PORT_FILE" 2>/dev/null)
if [ -z "$PORT" ]; then
  exit 0
fi

# Get CDP address by browser name (matches inject-cdp.sh)
BROWSER_NAME="default"
CDP_ADDRESS=$(cd "$CWD" && intunedctl dev browser status --json 2>/dev/null | jq -r --arg name "$BROWSER_NAME" '.browsers[] | select(.name == $name) | .cdpAddress // empty')
if [ -z "$CDP_ADDRESS" ]; then
  exit 0
fi

# Build tab map: {tabId: targetId} — lets the MCP server use real tab IDs for network log folders
TAB_MAP=$(cd "$CWD" && intunedctl dev browser tabs list --json 2>/dev/null | jq -c '.tabs | map({(.tabId): .targetId}) | add // {}')
TAB_MAP="${TAB_MAP:-"{}"}"

# Notify the MCP control server; failure is silent (best-effort)
curl -sf -X POST "http://127.0.0.1:${PORT}/browser/connect" \
  -H "Content-Type: application/json" \
  -d "{\"cdp_address\": \"$CDP_ADDRESS\", \"tab_map\": $TAB_MAP}" \
  > /dev/null 2>&1 || true

exit 0
