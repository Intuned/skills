#!/usr/bin/env bun

// Sync onCommandStart hook that injects a default -o (--output-file) inside
// .intuned-agent/ for `platform attempts trace` and `platform attempts log`
// when the user hasn't provided one.

import path from "node:path";
import {
  readHookInputFromStdin,
  toArray,
  toObject,
  toStringValue,
} from "./artifacts-common";

function sanitizePathSegment(value: string): string {
  return value.trim().replace(/[^a-zA-Z0-9._-]/g, "_");
}

const COMMANDS = [
  {
    prefix: ["platform", "attempts", "trace"],
    subcommand: "trace",
    defaultExt: "zip",
  },
  {
    prefix: ["platform", "attempts", "log"],
    subcommand: "log",
    defaultExt: "jsonl",
  },
] as const;

const input = readHookInputFromStdin();
if (!input) process.exit(0);

if (toStringValue(input.trigger) !== "onCommandStart") process.exit(0);

const commandArgs = Array.isArray(input.args)
  ? input.args.map((v) => String(v ?? ""))
  : [];

const matched = COMMANDS.find((cmd) =>
  cmd.prefix.every((token, index) => commandArgs[index] === token)
);
if (!matched) process.exit(0);

const payload = toObject(input.payload);
const argumentsValue = toArray(payload?.arguments);
const optionsValue = toObject(payload?.options);
if (!argumentsValue || !optionsValue) process.exit(0);

// Respect explicit user output path; only inject when missing.
const userOutputFile = toStringValue(optionsValue.outputFile);
if (userOutputFile) {
  process.exit(0);
}

// Build a default path inside .intuned-agent/.
const runId = sanitizePathSegment(commandArgs[3] || "unknown");
const attemptNumber = sanitizePathSegment(commandArgs[4] || "1");
const filename = `${matched.subcommand}_${runId}_${attemptNumber}.${matched.defaultExt}`;
const outputPath = path.join(
  ".intuned-agent",
  "platform-attempts",
  runId,
  filename
);

process.stdout.write(
  `${JSON.stringify({
    arguments: argumentsValue,
    options: { ...optionsValue, outputFile: outputPath },
    __log: `Output redirected to ${outputPath}`,
  })}\n`
);
process.exit(0);
