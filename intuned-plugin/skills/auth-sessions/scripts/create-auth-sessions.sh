#!/bin/bash

# Creates intuned-resources/auth-sessions/ from .parameters/auth-sessions/create/*.json
# Each credential file becomes one <name>.auth-session.json resource file.
# Credentials are written via printf redirection — values never appear in shell output.
# Usage: run from the project root

set -euo pipefail

PARAMS_DIR=".parameters/auth-sessions/create"
OUTPUT_DIR="intuned-resources/auth-sessions"

if [ ! -d "$PARAMS_DIR" ]; then
  echo "Error: $PARAMS_DIR not found. Are you running from the project root?"
  exit 1
fi

shopt -s nullglob
cred_files=("$PARAMS_DIR"/*.json)

if [ ${#cred_files[@]} -eq 0 ]; then
  echo "No credential files found in $PARAMS_DIR"
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

for cred_file in "${cred_files[@]}"; do
  name=$(basename "$cred_file" .json)
  params=$(cat "$cred_file")
  printf '{\n  "parameters": %s\n}\n' "$params" \
    > "$OUTPUT_DIR/${name}.auth-session.json"
  echo "Created $OUTPUT_DIR/${name}.auth-session.json"
done
