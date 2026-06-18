#!/usr/bin/env bun

import fs from "node:fs";
import path from "node:path";
import {
  SUPPORTED_TRIGGERS,
  classifyCommand,
  createRunDir,
  debugLog,
  ensureRunGroupDir,
  extractRunIdFromPlatformTestArgs,
  extractRunIdFromPlatformTriggerComplete,
  findActiveRunDirByPid,
  getInjectedToolUseId,
  getArtifactsRootDir,
  nowMs,
  obfuscateParameterValues,
  readHookInputFromStdin,
  toNumber,
  toObject,
  toStringValue,
  writeJson,
} from "./artifacts-common";

function safeReadJson(filePath: string): unknown {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

function ensureJsonFile(filePath: string, defaultValue: unknown): void {
  if (!fs.existsSync(filePath)) {
    writeJson(filePath, defaultValue);
  }
}

function appendJsonl(filePath: string, record: unknown): void {
  fs.appendFileSync(filePath, `${JSON.stringify(record)}\n`, "utf8");
}

function appendArrayField(
  filePath: string,
  field: string,
  item: unknown,
  defaultValue: Record<string, unknown>
): void {
  const parsed = toObject(safeReadJson(filePath)) ?? { ...defaultValue };
  const next = { ...parsed };
  const current = Array.isArray(next[field]) ? next[field] : [];
  next[field] = [...current, item];
  writeJson(filePath, next);
}

function readMetadata(
  filePath: string,
  defaultValue: Record<string, unknown>
): Record<string, unknown> {
  const parsed = toObject(safeReadJson(filePath));
  return {
    ...defaultValue,
    ...(parsed ?? {}),
  };
}

function extractCommandError(
  payloadObj: Record<string, unknown> | null
): { code?: string; message?: string } | null {
  const fromError = toObject(payloadObj?.error);
  const fromJsonOutput = toObject(payloadObj?.jsonOutput);
  const fromJsonOutputError = toObject(fromJsonOutput?.error);
  const errorObj = fromError ?? fromJsonOutputError ?? fromJsonOutput;

  if (!errorObj) {
    return null;
  }

  const code = toStringValue(errorObj.code);
  const message = toStringValue(errorObj.message);

  if (!code && !message) {
    return null;
  }

  return {
    ...(code ? { code } : {}),
    ...(message ? { message } : {}),
  };
}

function extractJsonOutputObject(
  payloadObj: Record<string, unknown> | null
): Record<string, unknown> | null {
  const jsonOutput = payloadObj?.jsonOutput;
  const jsonOutputObj = toObject(jsonOutput);
  if (jsonOutputObj) {
    return jsonOutputObj;
  }

  if (typeof jsonOutput !== "string") {
    return null;
  }

  try {
    return toObject(JSON.parse(jsonOutput));
  } catch {
    return null;
  }
}

function removeFileIfExists(filePath: string): void {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  } catch {
    // Best-effort only.
  }
}

function shouldObfuscateAttemptParameters(
  command: ReturnType<typeof classifyCommand>,
  payloadObj: Record<string, unknown>
): boolean {
  if (command?.kind === "authsession_create") {
    return true;
  }

  const apiName = toStringValue(payloadObj.api);
  return apiName.startsWith("auth-sessions/");
}

function parseTriggerParametersFromArgs(commandArgs: string[]): unknown {
  const afterTrigger = commandArgs.slice(3);
  if (afterTrigger.length === 0) {
    return null;
  }

  const fromJobIndex = afterTrigger.findIndex(
    (arg) => arg === "--from-job-config"
  );
  if (fromJobIndex >= 0 && afterTrigger[fromJobIndex + 1]) {
    return { fromJobConfig: afterTrigger[fromJobIndex + 1] };
  }

  const firstPositional = afterTrigger.find((arg) => !arg.startsWith("-"));
  if (!firstPositional) {
    return afterTrigger;
  }

  const trimmed = firstPositional.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      return JSON.parse(trimmed);
    } catch {
      return firstPositional;
    }
  }

  return firstPositional;
}

const input = readHookInputFromStdin();
if (!input) {
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

const trigger = toStringValue(input.trigger);
if (trigger === "onCommandStart") {
  process.exit(0);
}

if (!SUPPORTED_TRIGGERS.has(trigger)) {
  process.exit(0);
}

const pid = toNumber(input.pid, 0);
const cwd = toStringValue(input.cwd) || process.cwd();
const commandArgs = Array.isArray(input.args)
  ? input.args.map((value) => String(value ?? ""))
  : [];
const payload = input.payload ?? null;
const timestamp = nowMs();
const toolUseId = getInjectedToolUseId();

const isPlatformTestCommand =
  command.kind === "platform_test" || command.kind === "test_job";
const platformSubcommand = command.platformSubcommand;
let runId = "";
let runGroupDir: string | null = null;

if (isPlatformTestCommand && platformSubcommand) {
  if (platformSubcommand === "trigger") {
    if (trigger !== "onCommandComplete") {
      process.exit(0);
    }
    runId = extractRunIdFromPlatformTriggerComplete(payload);
  } else {
    runId = extractRunIdFromPlatformTestArgs(commandArgs);
  }
  if (!runId) {
    process.exit(0);
  }
  runGroupDir = ensureRunGroupDir(artifactsRoot, runId);
  if (!runGroupDir) {
    process.exit(0);
  }
  if (platformSubcommand === "trigger" && trigger === "onCommandComplete") {
    const runDirectory = `.artifacts/${runId}`;
    const parameters = parseTriggerParametersFromArgs(commandArgs);
    const metadataPath = path.join(runGroupDir, "metadata.json");

    writeJson(path.join(runGroupDir, "parameters.json"), parameters);
    writeJson(metadataPath, {
      version: 1,
      pid,
      cwd,
      commandArgs,
      commandType: command.commandType,
      startedAt: timestamp,
      status: "running",
      runId,
      runDirectory,
      parametersFile: `${runDirectory}/parameters.json`,
      injectedOptions: {},
      ...(toolUseId ? { toolUseId } : {}),
    });
  }
  if (platformSubcommand === "result" && trigger === "onCommandComplete") {
    const payloadObj = toObject(payload);
    const jsonOutputObj = extractJsonOutputObject(payloadObj);
    const resultStatus = toStringValue(jsonOutputObj?.status);
    const metadataPath = path.join(runGroupDir, "metadata.json");

    if (
      jsonOutputObj &&
      toStringValue(jsonOutputObj.runId) &&
      (resultStatus === "pending" ||
        resultStatus === "failed" ||
        resultStatus === "succeeded")
    ) {
      writeJson(path.join(runGroupDir, "result.json"), jsonOutputObj);

      const parsedMetadata = readMetadata(metadataPath, {
        version: 1,
        pid,
        cwd,
        commandArgs,
        commandType: command.commandType,
        startedAt: timestamp,
        status: "running",
        runId,
        runDirectory: `.artifacts/${runId}`,
        injectedOptions: {},
        ...(toolUseId ? { toolUseId } : {}),
      });

      parsedMetadata.runId = toStringValue(jsonOutputObj.runId, runId);
      parsedMetadata.status =
        resultStatus === "pending"
          ? "running"
          : resultStatus === "succeeded"
          ? "succeeded"
          : "failed";

      if (resultStatus === "pending") {
        delete parsedMetadata.completedAt;
      } else {
        parsedMetadata.completedAt = timestamp;
      }

      writeJson(metadataPath, parsedMetadata);
    }
  }
  // For platform test, keep only run root artifacts and skip per-command files.
  process.exit(0);
}

let runDir: string | null = null;
if (!isPlatformTestCommand) {
  runDir = findActiveRunDirByPid(artifactsRoot, pid);
  if (!runDir) {
    // Fallback path: recover by creating a run if start mutation hook did not
    // initialize one (defensive for partial hook registration).
    runDir = createRunDir(artifactsRoot, command.commandSlug);
  }
}

if (!runDir || !fs.existsSync(runDir)) {
  process.exit(0);
}

const parametersPath = path.join(runDir, "parameters.json");
const logsPath = path.join(runDir, "logs.jsonl");
const resultPath = path.join(runDir, "result.json");
const errorPath = path.join(runDir, "error.json");
const metadataPath = path.join(runDir, "metadata.json");
const runDirectory = `.artifacts/${path.basename(runDir)}`;

if (!fs.existsSync(metadataPath)) {
  writeJson(metadataPath, {
    version: 1,
    pid,
    cwd,
    commandArgs,
    commandType: command.commandType,
    startedAt: timestamp,
    status: "running",
    runDirectory,
    recoveredFromTrigger: trigger,
    injectedOptions: {},
    ...(toolUseId ? { toolUseId } : {}),
    ...(runId ? { runId } : {}),
  });
}

ensureJsonFile(parametersPath, {
  command: commandArgs.slice(3),
  attempts: [],
});
if (!fs.existsSync(logsPath)) {
  fs.writeFileSync(logsPath, "", "utf8");
}
ensureJsonFile(resultPath, {
  attemptCompletions: [],
  commandComplete: null,
});

const metadata = toObject(safeReadJson(metadataPath)) ?? {};
const outputFile = toStringValue(metadata.outputFile);
const skipManagedResultWrites =
  // If CLI output is already directed to this file, avoid writing our own
  // structured snapshot on top of the downloaded/output payload.
  outputFile.length > 0 && outputFile === path.join(runDir, "result.json");

debugLog(
  `events-capture: trigger=${trigger} command=${command.commandType} runDir=${runDir}`
);

if (trigger === "onAttemptStart") {
  const payloadObj = toObject(payload);
  if (
    payloadObj &&
    Object.prototype.hasOwnProperty.call(payloadObj, "parameters")
  ) {
    const shouldObfuscate = shouldObfuscateAttemptParameters(
      command,
      payloadObj
    );
    const parametersValue = shouldObfuscate
      ? obfuscateParameterValues(payloadObj.parameters)
      : payloadObj.parameters;

    appendArrayField(parametersPath, "attempts", parametersValue, {
      command: [],
      attempts: [],
    });
  }

  if (command.kind === "api") {
    const authSessionId = toStringValue(payloadObj?.authSessionId);
    if (authSessionId) {
      const parsedMetadata = toObject(safeReadJson(metadataPath)) ?? {};
      parsedMetadata.authSessionId = authSessionId;
      writeJson(metadataPath, parsedMetadata);
    }
  }
  process.exit(0);
}

if (trigger === "onAttemptCompleted") {
  const payloadObj = toObject(payload);
  const attemptLogs = Array.isArray(payloadObj?.logs) ? payloadObj.logs : [];
  const attemptNumber = toNumber(payloadObj?.attemptNumber);
  const totalAttempts = toNumber(payloadObj?.totalAttempts);
  const status = toStringValue(payloadObj?.status);
  const metadataDefaults = {
    version: 1,
    pid,
    cwd,
    commandArgs,
    commandType: command.commandType,
    startedAt: timestamp,
    status: "running",
    runDirectory,
    injectedOptions: {},
    ...(toolUseId ? { toolUseId } : {}),
    ...(runId ? { runId } : {}),
  };

  if (attemptLogs.length > 0) {
    for (const logEntry of attemptLogs) {
      appendJsonl(logsPath, {
        type: "attempt_log",
        timestamp,
        commandType: command.commandType,
        attemptNumber,
        totalAttempts,
        status,
        log: logEntry,
      });
    }
  }

  const parsedMetadata = readMetadata(metadataPath, metadataDefaults);
  const isFinalAttempt =
    attemptNumber > 0 && totalAttempts > 0
      ? attemptNumber >= totalAttempts
      : false;

  parsedMetadata.status =
    status === "failed" && isFinalAttempt
      ? "failed"
      : status === "succeeded" && isFinalAttempt
      ? "succeeded"
      : "running";
  writeJson(metadataPath, parsedMetadata);

  if (isFinalAttempt) {
    const commandError =
      status === "failed" ? extractCommandError(payloadObj) : null;

    if (commandError) {
      writeJson(errorPath, commandError);
    } else {
      removeFileIfExists(errorPath);
    }
  }

  if (!skipManagedResultWrites) {
    appendArrayField(
      resultPath,
      "attemptCompletions",
      { timestamp, payload },
      {
        attemptCompletions: [],
        commandComplete: null,
      }
    );
  }

  process.exit(0);
}

if (trigger === "onCommandComplete") {
  const payloadObj = toObject(payload);
  appendJsonl(logsPath, {
    type: "command_complete",
    timestamp,
    commandType: command.commandType,
    trigger,
    exitCode: toNumber(payloadObj?.exitCode),
    authErrorOccurred: Boolean(payloadObj?.authErrorOccurred),
  });

  if (!skipManagedResultWrites) {
    const parsedResult = toObject(safeReadJson(resultPath)) ?? {
      attemptCompletions: [],
      commandComplete: null,
    };
    parsedResult.commandComplete = {
      timestamp,
      payload,
      outputFile,
    };
    writeJson(resultPath, parsedResult);
  }

  const parsedMetadata = readMetadata(metadataPath, {
    version: 1,
    pid,
    cwd,
    commandArgs,
    commandType: command.commandType,
    startedAt: timestamp,
    status: "running",
    runDirectory,
    injectedOptions: {},
    ...(toolUseId ? { toolUseId } : {}),
    ...(runId ? { runId } : {}),
  });
  const exitCode = toNumber(payloadObj?.exitCode);
  const alreadyFailed = parsedMetadata.status === "failed";
  parsedMetadata.status =
    alreadyFailed || exitCode !== 0 ? "failed" : "succeeded";
  parsedMetadata.completedAt = timestamp;
  writeJson(metadataPath, parsedMetadata);

  if (parsedMetadata.status === "succeeded") {
    removeFileIfExists(errorPath);
  } else if (!fs.existsSync(errorPath)) {
    const commandError = extractCommandError(payloadObj);
    if (commandError) {
      writeJson(errorPath, commandError);
    }
  }
}
