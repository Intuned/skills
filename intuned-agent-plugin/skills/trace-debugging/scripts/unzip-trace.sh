#!/bin/bash

# Script to unzip trace files, handling existing directories
# Usage: ./unzip-trace.sh <trace-file.zip>

if [ -z "$1" ]; then
  echo "Error: No trace file specified"
  echo "Usage: $0 <trace-file.zip>"
  exit 1
fi

TRACE_FILE="$1"
BASE_DIR=".intuned-agent/playwright-traces"

# Check if trace file exists
if [ ! -f "$TRACE_FILE" ]; then
  echo "Error: Trace file not found: $TRACE_FILE"
  exit 1
fi

# Extract the trace name from the file path (without .zip extension)
TRACE_NAME=$(basename "$TRACE_FILE" .zip)
EXTRACT_DIR="$BASE_DIR/$TRACE_NAME"

# Create base directory if it doesn't exist
mkdir -p "$BASE_DIR"

# Remove only this specific trace extraction if it exists
if [ -d "$EXTRACT_DIR" ]; then
  rm -rf "$EXTRACT_DIR"
fi

# Unzip the trace file quietly
unzip -q "$TRACE_FILE" -d "$EXTRACT_DIR"

if [ $? -eq 0 ]; then
  echo "Successfully extracted to: $EXTRACT_DIR"
else
  echo "Error: Failed to extract $TRACE_FILE"
  exit 1
fi
