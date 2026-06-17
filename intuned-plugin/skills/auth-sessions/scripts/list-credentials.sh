#!/bin/bash

# Lists stored credential parameter files and their field names (never values).
# Usage: ./list-credentials.sh

DIR=".parameters/auth-sessions/create"

if [ ! -d "$DIR" ] || [ -z "$(ls "$DIR"/*.json 2>/dev/null)" ]; then
  echo "No credentials stored yet."
  exit 0
fi

echo "Stored credentials:"
for f in "$DIR"/*.json; do
  name=$(basename "$f" .json)
  fields=$(python3 -c "import json,sys; print(', '.join(json.load(open(sys.argv[1])).keys()))" "$f" 2>/dev/null || echo "(unable to read fields)")
  echo "- name: $name, fields: $fields"
done
