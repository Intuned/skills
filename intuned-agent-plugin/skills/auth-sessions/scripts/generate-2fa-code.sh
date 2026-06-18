#!/bin/bash

# Generates a fresh 2FA TOTP code from a stored credential param file, using the
# library that matches the project language: otpauth (Node/TypeScript) or pyotp
# (Python). When there is no project yet (planning), it falls back to an ephemeral
# Python runner that installs nothing into the project.
#
# The TOTP secret is read inside the runtime and is NEVER printed or passed on the
# command line. Only the current 6-digit code is written to stdout.
#
# Usage: ./generate-2fa-code.sh [path-to-param.json] [secret-key]
#   path-to-param.json  default: .parameters/auth-sessions/create/default.json
#   secret-key          JSON key holding the TOTP secret (default: otpSecret)

set -euo pipefail

PARAM_FILE="${1:-.parameters/auth-sessions/create/default.json}"
KEY="${2:-otpSecret}"

if [ ! -f "$PARAM_FILE" ]; then
  echo "Param file not found: $PARAM_FILE" >&2
  exit 1
fi

# Runtimes read the file at argv[1] and the key at argv[2]; the secret never touches argv.
PY_CODE='import json,sys,pyotp; print(pyotp.TOTP(json.load(open(sys.argv[1]))[sys.argv[2]]).now())'
JS_CODE='const OTPAuth=require("otpauth");const creds=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));console.log(new OTPAuth.TOTP({secret:creds[process.argv[2]]}).generate());'

if [ -f "package.json" ]; then
  # Node / TypeScript project -> otpauth
  if node -e 'require.resolve("otpauth")' >/dev/null 2>&1; then
    node -e "$JS_CODE" "$PARAM_FILE" "$KEY"
  else
    # otpauth not installed yet: install into a throwaway dir, don't touch the project.
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    npm install --prefix "$TMP_DIR" otpauth >/dev/null 2>&1
    NODE_PATH="$TMP_DIR/node_modules" node -e "$JS_CODE" "$PARAM_FILE" "$KEY"
  fi
else
  # Python project or no project yet -> pyotp via uv (ephemeral, no project mutation).
  uv run --with pyotp python -c "$PY_CODE" "$PARAM_FILE" "$KEY"
fi