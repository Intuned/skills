#!/usr/bin/env bun

import fs from "node:fs";
import path from "node:path";
import {
  classifyCommand,
  createRunDir,
  debugLog,
  ensureRunGroupDir,
  extractRunIdFromPlatformTestArgs,
  getInjectedToolUseId,
  getArtifactsRootDir,
  nowMs,
  obfuscateParameterValues,
  readHookInputFromStdin,
  resolveOutputPath,
  toArray,
  toNumber,
  toObject,
  toStringValue,
  writeJson,
} from "./artifacts-common";

function obfuscateAuthCreateCommandParameters(
  argumentsValue: unknown[]
): unknown[] {
  return argumentsValue.map((value, index) => {
    // Keep the authsession subcommand token ("create") readable.
    if (index === 0) {
      return value;
    }

    if (typeof value !== "string") {
      return obfuscateParameterValues(value);
    }

    const trimmed = value.trim();
    if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) {
      return value;
    }

    try {
      const parsed = JSON.parse(trimmed);
      return JSON.stringify(obfuscateParameterValues(parsed));
    } catch {
      return value;
    }
  });
}

const input = readHookInputFromStdin();
if (!input) {
  process.exit(0);
}

// This hook runs synchronously and can mutate CLI args/options.
if (toStringValue(input.trigger) !== "onCommandStart") {
  process.exit(0);
}

const artifactsRoot = getArtifactsRootDir();
if (!artifactsRoot) {
  process.exit(0);
}

const command = classifyCommand(input);
if (!command) {
  process.exit(0);
}

const payload = toObject(input.payload);
if (!payload) {
  process.exit(0);
}

const argumentsValue = toArray(payload.arguments);
const optionsValue = toObject(payload.options);
if (!argumentsValue || !optionsValue) {
  process.exit(0);
}

function writeMutationAndExit(options: Record<string, unknown>, log?: string): never {
  const output: Record<string, unknown> = {
    arguments: argumentsValue,
    options,
  };
  if (log) {
    output.__log = log;
  }
  process.stdout.write(`${JSON.stringify(output)}\n`);
  process.exit(0);
}

const pid = toNumber(input.pid, 0);
const cwd = toStringValue(input.cwd) || process.cwd();
const startedAt = nowMs();
const toolUseId = getInjectedToolUseId();
const commandArgs = Array.isArray(input.args)
  ? input.args.map((value) => String(value ?? ""))
  : [];
const isPlatformTestCommand =
  command.kind === "platform_test" || command.kind === "test_job";
const platformSubcommand = command.platformSubcommand;
let runId = "";

let runDir = "";
if (!isPlatformTestCommand) {
  const created = createRunDir(artifactsRoot, command.commandSlug);
  runDir = created ?? "";
}

const effectiveOptions: Record<string, unknown> = {
  ...optionsValue,
  quiet: true,
};
const injectedOptions: Record<string, unknown> = {};

if (optionsValue.quiet !== true) {
  injectedOptions.quiet = true;
}

let effectiveOutputFile = "";
const userOutputFile = toStringValue(optionsValue.outputFile);
let outputFileOptionValue = "";
let effectiveTracesPath = "";
const userTracesPath = toStringValue(optionsValue.tracesPath);

if (command.supportsOutput) {
  // Respect explicit user output path; only inject when missing.
  if (userOutputFile) {
    effectiveOutputFile = resolveOutputPath(cwd, userOutputFile);
    outputFileOptionValue = userOutputFile;
  } else if (command.injectedOutputFilename) {
    if (isPlatformTestCommand && platformSubcommand === "download") {
      runId = extractRunIdFromPlatformTestArgs(commandArgs);
      const runGroupDir = ensureRunGroupDir(artifactsRoot, runId);
      if (runGroupDir) {
        effectiveOutputFile = path.join(runGroupDir, "downloaded-result.jsonl");
        outputFileOptionValue = effectiveOutputFile;
      }
    } else if (runDir) {
      effectiveOutputFile = path.join(runDir, command.injectedOutputFilename);
      outputFileOptionValue = effectiveOutputFile;
    }
  }
  if (outputFileOptionValue) {
    effectiveOptions.outputFile = outputFileOptionValue;
  }
  if (!userOutputFile && outputFileOptionValue) {
    injectedOptions.outputFile = outputFileOptionValue;
  }
}

if (command.supportsTrace && optionsValue.trace === true) {
  if (userTracesPath) {
    effectiveTracesPath = resolveOutputPath(cwd, userTracesPath);
  } else if (runDir) {
    // intunedctl treats tracesPath as a directory and writes zip files under it,
    // so point it at the run root to keep traces flat beside the other artifacts.
    effectiveTracesPath = runDir;
    effectiveOptions.tracesPath = effectiveTracesPath;
    injectedOptions.tracesPath = effectiveTracesPath;
  }
}

if (isPlatformTestCommand) {
  const log =
    platformSubcommand === "download" && effectiveOutputFile
      ? `Artifacts: downloaded-results=${effectiveOutputFile}. Result may be large; use the read tool with a small limit first.`
      : undefined;
  writeMutationAndExit(effectiveOptions, log);
}

if (!runDir) {
  // `platform test trigger` is intentionally captured at command complete only
  // (when runId becomes available), so start hook writes no files here.
  writeMutationAndExit(effectiveOptions);
}

const runName = path.basename(runDir);
const runDirectory = runId
  ? `.artifacts/${runId}/${runName}`
  : `.artifacts/${runName}`;
const parametersFile = `${runDirectory}/parameters.json`;
const logsFile = `${runDirectory}/logs.jsonl`;
const resultFile = `${runDirectory}/result.json`;

const metadata: Record<string, unknown> = {
  version: 1,
  pid,
  cwd,
  commandArgs,
  commandType: command.commandType,
  startedAt,
  status: "running",
  runDirectory,
  parametersFile,
  logsFile,
  resultFile,
  injectedOptions,
};

if (toolUseId) {
  metadata.toolUseId = toolUseId;
}

if (command.kind === "api") {
  const authSessionId = toStringValue(optionsValue.authSession);
  if (authSessionId) {
    metadata.authSessionId = authSessionId;
  }
}

if (runId) {
  metadata.runId = runId;
}

if (effectiveOutputFile) {
  metadata.outputFile = effectiveOutputFile;
}
if (effectiveTracesPath) {
  metadata.tracesPath = effectiveTracesPath;
  try {
    fs.mkdirSync(effectiveTracesPath, { recursive: true });
  } catch {
    // Best-effort only: trace writer may still create folders lazily.
  }
}

const parameters = {
  // Keep this file focused on user-supplied command parameters only.
  command:
    command.kind === "authsession_create"
      ? obfuscateAuthCreateCommandParameters(argumentsValue)
      : argumentsValue,
  attempts: [],
};

const result = {
  attemptCompletions: [],
  commandComplete: null,
};

debugLog(`start-mutation: writing artifacts to ${runDir} (command=${command.commandType})`);
writeJson(path.join(runDir, "metadata.json"), metadata);
writeJson(path.join(runDir, "parameters.json"), parameters);
fs.writeFileSync(path.join(runDir, "logs.jsonl"), "", "utf8");

if (effectiveOutputFile !== path.join(runDir, "result.json")) {
  writeJson(path.join(runDir, "result.json"), result);
}

const logsPathForHint = path.join(runDir, "logs.jsonl");

// stdout JSON is consumed by intunedctl as the mutated command payload.
writeMutationAndExit(
  effectiveOptions,
  `Artifacts: logs=${logsPathForHint}. Result may be large; use the read tool with a small limit first.`
);
