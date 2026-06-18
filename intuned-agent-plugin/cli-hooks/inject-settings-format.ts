#!/usr/bin/env bun

// Sync onCommandStart hook that injects settingsFormat: "json" into options for
// dev init / dev stealth / dev captcha-solve / dev proxy commands.

import {
  readHookInputFromStdin,
  toArray,
  toObject,
  toStringValue,
} from "./artifacts-common";

const SETTINGS_FORMAT_PREFIXES = [
  ["dev", "init"],
  ["dev", "stealth"],
  ["dev", "captcha-solve"],
  ["dev", "proxy"],
] as const;

const input = readHookInputFromStdin();
if (!input) process.exit(0);

if (toStringValue(input.trigger) !== "onCommandStart") process.exit(0);

const commandArgs = Array.isArray(input.args)
  ? input.args.map((v) => String(v ?? ""))
  : [];

const matches = SETTINGS_FORMAT_PREFIXES.some((prefix) =>
  prefix.every((token, index) => commandArgs[index] === token)
);
if (!matches) process.exit(0);

const payload = toObject(input.payload);
const argumentsValue = toArray(payload?.arguments);
const optionsValue = toObject(payload?.options);
if (!argumentsValue || !optionsValue) process.exit(0);

if (optionsValue.settingsFormat) process.exit(0);

process.stdout.write(
  `${JSON.stringify({
    arguments: argumentsValue,
    options: { ...optionsValue, settingsFormat: "json" },
  })}\n`
);
process.exit(0);
