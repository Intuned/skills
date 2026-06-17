#!/bin/bash

# Debug log file
DEBUG_LOG="/tmp/inject-cdp-debug.log"

# Read hook input from stdin
INPUT=$(cat)

echo "$(date): Hook called" >> "$DEBUG_LOG"
echo "INPUT: $INPUT" >> "$DEBUG_LOG"

# Use CLAUDE_SDK_WORKING_DIRECTORY (static project root) instead of .cwd from hook input,
# because .cwd changes when the agent runs `cd` and would break CLI lookups.
CWD="${CLAUDE_SDK_WORKING_DIRECTORY:-$(echo "$INPUT" | jq -r '.cwd')}"
BROWSER_NAME="default"
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input')

echo "$(date): Extracted CWD: $CWD" >> "$DEBUG_LOG"
echo "$(date): Extracted BROWSER_NAME: $BROWSER_NAME" >> "$DEBUG_LOG"
echo "$(date): Extracted TOOL_INPUT: $TOOL_INPUT" >> "$DEBUG_LOG"

# Build target ID map from browser tabs (default to empty object)
TARGET_ID_MAP="{}"
echo "$(date): Fetching browser tabs for target ID mapping" >> "$DEBUG_LOG"

TABS_OUTPUT=$(cd "$CWD" && intunedctl dev browser tabs list --json 2>> "$DEBUG_LOG")
TABS_EXIT_CODE=$?

if [ $TABS_EXIT_CODE -eq 0 ]; then
  echo "$(date): Browser tabs list command succeeded" >> "$DEBUG_LOG"
  echo "$(date): Tabs output: $TABS_OUTPUT" >> "$DEBUG_LOG"

  # Build map of tabId -> targetId
  TARGET_ID_MAP=$(echo "$TABS_OUTPUT" | jq -c '.tabs | map({(.tabId): .targetId}) | add // {}')

  echo "$(date): Built target ID map: $TARGET_ID_MAP" >> "$DEBUG_LOG"
else
  echo "$(date): Browser tabs list command failed with exit code $TABS_EXIT_CODE, using empty map" >> "$DEBUG_LOG"
fi

# Get browser status from CLI
echo "$(date): Fetching browser status for CDP address" >> "$DEBUG_LOG"

STATUS_OUTPUT=$(cd "$CWD" && intunedctl dev browser status --json 2>> "$DEBUG_LOG")
STATUS_EXIT_CODE=$?

if [ $STATUS_EXIT_CODE -eq 0 ]; then
  echo "$(date): Browser status command succeeded" >> "$DEBUG_LOG"
  echo "$(date): Status output: $STATUS_OUTPUT" >> "$DEBUG_LOG"

  # Extract CDP address for the named browser
  CDP_ADDRESS=$(echo "$STATUS_OUTPUT" | jq -r --arg name "$BROWSER_NAME" '.browsers[] | select(.name == $name) | .cdpAddress // empty')
  echo "$(date): CDP_ADDRESS: $CDP_ADDRESS" >> "$DEBUG_LOG"

  # Check if the browser process is actually running
  RUNNING=$(echo "$STATUS_OUTPUT" | jq -r --arg name "$BROWSER_NAME" '.browsers[] | select(.name == $name) | .running')
  if [ "$RUNNING" != "true" ]; then
    echo "$(date): Browser is not running, blocking tool" >> "$DEBUG_LOG"
    jq -n '{
      "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Browser is closed. Please start the browser."
      }
    }'
    echo "$(date): Hook done (browser not running)" >> "$DEBUG_LOG"
    exit 0
  fi

  if [ -n "$CDP_ADDRESS" ]; then
    echo "$(date): CDP address found, injecting into tool input" >> "$DEBUG_LOG"

    # Check for auth params directory
    AUTH_PARAMS_DIR=""
    AUTH_PARAMS_DIR_PATH="$CWD/.parameters/auth-sessions/create"
    if [ -d "$AUTH_PARAMS_DIR_PATH" ]; then
      AUTH_PARAMS_DIR="$AUTH_PARAMS_DIR_PATH"
      echo "$(date): Auth params directory found: $AUTH_PARAMS_DIR" >> "$DEBUG_LOG"
    fi

    # Output updated input with CDP address, target ID map, and optional auth params directory
    jq -n \
      --arg cdp "$CDP_ADDRESS" \
      --argjson target_map "$TARGET_ID_MAP" \
      --arg auth_dir "$AUTH_PARAMS_DIR" \
      --argjson input "$TOOL_INPUT" \
      '{
        "hookSpecificOutput": {
          "hookEventName": "PreToolUse",
          "permissionDecision": "allow",
          "updatedInput": ($input + {"hidden_cdp_address": $cdp, "hidden_target_id_map": $target_map} + (if $auth_dir != "" then {"hidden_auth_params_dir": $auth_dir} else {} end))
        }
      }'
    echo "$(date): Output JSON response with CDP address, target ID map, and auth params dir" >> "$DEBUG_LOG"
  else
    # No CDP address found - let the tool handle it
    echo "$(date): CDP address is empty or browser not found, returning empty response" >> "$DEBUG_LOG"
    echo '{}'
  fi
else
  echo "$(date): Browser status command failed with exit code $STATUS_EXIT_CODE, denying tool" >> "$DEBUG_LOG"
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "Browser is closed. Please restart the browser."
    }
  }'
fi

echo "$(date): Hook execution completed" >> "$DEBUG_LOG"
