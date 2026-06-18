#!/usr/bin/env bun

// onCommandStart hook: injects --non-interactive into platform attempts get/log/trace
// so the CLI always runs without interactive prompts when invoked from the agent.
// If the attempt number is missing, the CLI will surface a clean error itself.

import { readHookInputFromStdin, toArray, toObject, toStringValue } from "./artifacts-common";

const COMMANDS = [
  { prefix: ["platform", "attempts", "trace"] },
  { prefix: ["platform", "attempts", "log"] },
  { prefix: ["platform", "attempts", "get"] },
] as const;

const input = readHookInputFromStdin();
if (!input) process.exit(0);

if (toStringValue(input.trigger) !== "onCommandStart") process.exit(0);

const args = Array.isArray(input.args) ? input.args.map((a) => String(a ?? "")) : [];

const matched = COMMANDS.find((cmd) => cmd.prefix.every((token, index) => args[index] === token));
if (!matched) process.exit(0);

const payload = toObject(input.payload);
const argumentsValue = toArray(payload?.arguments);
const optionsValue = toObject(payload?.options);
if (!argumentsValue || !optionsValue) process.exit(0);

// Already non-interactive — nothing to do
if (optionsValue.nonInteractive) process.exit(0);

process.stdout.write(
  `${JSON.stringify({
    arguments: argumentsValue,
    options: { ...optionsValue, nonInteractive: true },
  })}\n`
);
process.exit(0);
