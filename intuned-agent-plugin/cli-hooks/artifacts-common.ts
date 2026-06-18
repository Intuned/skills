#!/usr/bin/env bun

import fs from "node:fs";
import path from "node:path";

export type HookInput = {
  trigger?: unknown;
  pid?: unknown;
  cwd?: unknown;
  args?: unknown;
  payload?: {
    arguments?: unknown;
    options?: unknown;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};

export type CommandInfo = {
  commandType: string;
  commandSlug: string;
  kind:
    | "api"
    | "authsession_create"
    | "authsession_check"
    | "platform_test"
    | "test_job";
  supportsOutput: boolean;
  supportsTrace: boolean;
  platformSubcommand?: "trigger" | "result" | "download";
  injectedOutputFilename?: string;
};

type CommandDefinition = {
  argvPrefix: readonly string[];
} & CommandInfo;

export const SUPPORTED_TRIGGERS = new Set([
  "onAttemptStart",
  "onAttemptCompleted",
  "onCommandComplete",
]);

const COMMAND_DEFINITIONS: readonly CommandDefinition[] = [
  {
    argvPrefix: ["dev", "attempt", "api"],
    commandType: "dev_attempt_api",
    commandSlug: "dev-attempt-api",
    kind: "api",
    supportsOutput: true,
    supportsTrace: true,
    injectedOutputFilename: "result.json",
  },
  {
    argvPrefix: ["dev", "run", "api"],
    commandType: "dev_run_api",
    commandSlug: "dev-run-api",
    kind: "api",
    supportsOutput: true,
    supportsTrace: true,
    injectedOutputFilename: "result.json",
  },
  {
    argvPrefix: ["dev", "attempt", "authsession", "create"],
    commandType: "dev_attempt_authsession_create",
    commandSlug: "dev-attempt-authsession-create",
    kind: "authsession_create",
    supportsOutput: false,
    supportsTrace: true,
  },
  {
    argvPrefix: ["dev", "run", "authsession", "create"],
    commandType: "dev_run_authsession_create",
    commandSlug: "dev-run-authsession-create",
    kind: "authsession_create",
    supportsOutput: false,
    supportsTrace: true,
  },
  {
    argvPrefix: ["dev", "attempt", "authsession", "check"],
    commandType: "dev_attempt_authsession_check",
    commandSlug: "dev-attempt-authsession-check",
    kind: "authsession_check",
    supportsOutput: false,
    supportsTrace: true,
  },
  {
    argvPrefix: ["platform", "test", "trigger"],
    commandType: "platform_test_trigger",
    commandSlug: "platform-test-trigger",
    kind: "platform_test",
    platformSubcommand: "trigger",
    supportsOutput: false,
    supportsTrace: false,
  },
  {
    argvPrefix: ["platform", "test", "result"],
    commandType: "platform_test_result",
    commandSlug: "platform-test-result",
    kind: "platform_test",
    platformSubcommand: "result",
    supportsOutput: false,
    supportsTrace: false,
  },
  {
    argvPrefix: ["platform", "test", "download"],
    commandType: "platform_test_download",
    commandSlug: "platform-test-download",
    kind: "platform_test",
    platformSubcommand: "download",
    supportsOutput: true,
    supportsTrace: false,
    injectedOutputFilename: "downloaded-result.jsonl",
  },
  {
    argvPrefix: ["dev", "test-job", "trigger"],
    commandType: "dev_test_job_trigger",
    commandSlug: "dev-test-job-trigger",
    kind: "test_job",
    platformSubcommand: "trigger",
    supportsOutput: false,
    supportsTrace: false,
  },
  {
    argvPrefix: ["dev", "test-job", "result"],
    commandType: "dev_test_job_result",
    commandSlug: "dev-test-job-result",
    kind: "test_job",
    platformSubcommand: "result",
    supportsOutput: false,
    supportsTrace: false,
  },
  {
    argvPrefix: ["dev", "test-job", "download"],
    commandType: "dev_test_job_download",
    commandSlug: "dev-test-job-download",
    kind: "test_job",
    platformSubcommand: "download",
    supportsOutput: true,
    supportsTrace: false,
    injectedOutputFilename: "downloaded-result.jsonl",
  },
] as const;

export function readHookInputFromStdin(): HookInput | null {
  try {
    const raw = fs.readFileSync(0, "utf8");
    if (!raw.trim()) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return null;
    }
    return parsed as HookInput;
  } catch {
    return null;
  }
}

export function debugLog(message: string): void {
  const logFile = process.env.ARTIFACTS_HOOKS_DEBUG_LOG;
  if (!logFile) return;
  try {
    const timestamp = new Date().toISOString();
    fs.appendFileSync(logFile, `[${timestamp}] ${message}\n`, "utf8");
  } catch {
    // best-effort
  }
}

export function getArtifactsRootDir(): string | null {
  const artifactsDir = process.env.INTUNED_ARTIFACTS_DIR;
  if (!artifactsDir) {
    debugLog("getArtifactsRootDir: INTUNED_ARTIFACTS_DIR not set");
    return null;
  }

  try {
    fs.mkdirSync(artifactsDir, { recursive: true });
    debugLog(`getArtifactsRootDir: using ${artifactsDir}`);
    return artifactsDir;
  } catch {
    debugLog(`getArtifactsRootDir: failed to create ${artifactsDir}`);
    return null;
  }
}

function normalizeArgs(args: unknown): string[] {
  if (!Array.isArray(args)) {
    return [];
  }
  return args.map((value) => String(value ?? ""));
}

export function classifyCommand(input: HookInput): CommandInfo | null {
  const args = normalizeArgs(input.args);

  for (const definition of COMMAND_DEFINITIONS) {
    const matches = definition.argvPrefix.every(
      (token, index) => args[index] === token
    );
    if (matches) {
      return {
        commandType: definition.commandType,
        commandSlug: definition.commandSlug,
        kind: definition.kind,
        supportsOutput: definition.supportsOutput,
        supportsTrace: definition.supportsTrace,
        platformSubcommand: definition.platformSubcommand,
        injectedOutputFilename: definition.injectedOutputFilename,
      };
    }
  }

  return null;
}

export function nowMs(): number {
  return Date.now();
}

export function getInjectedToolUseId(): string {
  return (process.env.INTUNED_TOOL_USE_ID ?? "").trim();
}

function folderTimestamp(): string {
  return new Date()
    .toISOString()
    .replace(/\.\d{3}Z$/, "Z")
    .replace(/:/g, "-");
}

function sanitizeRunId(runId: string): string {
  return runId.trim().replace(/[^a-zA-Z0-9._-]/g, "_");
}

export function extractRunIdFromPlatformTestArgs(args: string[]): string {
  // CLI shape: platform test <subcommand> <run-id> [...]
  return sanitizeRunId(args[3] ?? "");
}

export function extractRunIdFromPlatformTriggerComplete(
  payload: unknown
): string {
  const payloadObj = toObject(payload);
  if (!payloadObj) {
    return "";
  }

  const jsonOutput = payloadObj.jsonOutput;
  if (typeof jsonOutput === "string") {
    try {
      const parsed = JSON.parse(jsonOutput);
      const parsedObj = toObject(parsed);
      if (!parsedObj) {
        return "";
      }
      return sanitizeRunId(toStringValue(parsedObj.runId));
    } catch {
      return "";
    }
  }

  const jsonOutputObj = toObject(jsonOutput);
  if (!jsonOutputObj) {
    return "";
  }

  return sanitizeRunId(toStringValue(jsonOutputObj.runId));
}

export function ensureRunGroupDir(
  artifactsRoot: string,
  runId: string
): string | null {
  if (!runId) {
    return null;
  }

  const groupDir = path.join(artifactsRoot, runId);
  try {
    fs.mkdirSync(groupDir, { recursive: true });
    return groupDir;
  } catch {
    return null;
  }
}

export function createInvocationDir(
  parentDir: string,
  subcommand: string
): string | null {
  try {
    const base = `${folderTimestamp()}-${subcommand}`;
    let runName = base;
    let suffix = 0;

    while (fs.existsSync(path.join(parentDir, runName))) {
      suffix += 1;
      runName = `${base}-${suffix}`;
    }

    const runDir = path.join(parentDir, runName);
    fs.mkdirSync(runDir, { recursive: true });
    return runDir;
  } catch {
    return null;
  }
}

export function createRunDir(
  artifactsRoot: string,
  slug: string
): string | null {
  try {
    // Folder shape: <ISO-timestamp>-<command-slug>[-N] on collision.
    const base = `${folderTimestamp()}-${slug}`;
    let runName = base;
    let suffix = 0;

    while (fs.existsSync(path.join(artifactsRoot, runName))) {
      suffix += 1;
      runName = `${base}-${suffix}`;
    }

    const runDir = path.join(artifactsRoot, runName);
    fs.mkdirSync(runDir, { recursive: true });
    return runDir;
  } catch {
    return null;
  }
}

function safeReadJson(filePath: string): unknown {
  try {
    const raw = fs.readFileSync(filePath, "utf8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function findActiveRunDirByPid(
  artifactsRoot: string,
  pid: number
): string | null {
  try {
    // Find the latest incomplete run for this process so event hooks can append
    // to the same folder that was initialized at command start.
    const entries = fs
      .readdirSync(artifactsRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort((left, right) => right.localeCompare(left));

    for (const name of entries) {
      const runDir = path.join(artifactsRoot, name);
      const metadataPath = path.join(runDir, "metadata.json");
      if (!fs.existsSync(metadataPath)) {
        continue;
      }

      const metadata = safeReadJson(metadataPath);
      if (!metadata || typeof metadata !== "object") {
        continue;
      }

      const metadataPid = Number((metadata as { pid?: unknown }).pid);
      const completedAt = (metadata as { completedAt?: unknown }).completedAt;

      if (metadataPid === pid && completedAt == null) {
        return runDir;
      }
    }
  } catch {
    return null;
  }

  return null;
}

export function writeJson(filePath: string, value: unknown): void {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 0)}\n`, "utf8");
}

export function resolveOutputPath(cwd: string, outputFile: string): string {
  if (!outputFile) {
    return "";
  }
  if (path.isAbsolute(outputFile)) {
    return outputFile;
  }
  return path.join(cwd, outputFile);
}

export function toObject(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

export function toArray(value: unknown): unknown[] | null {
  if (!Array.isArray(value)) {
    return null;
  }
  return value;
}

export function toNumber(value: unknown, fallback = 0): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function toStringValue(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

export function obfuscateParameterValues(value: unknown): unknown {
  if (value == null) {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map((entry) => obfuscateParameterValues(entry));
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    return Object.fromEntries(
      entries.map(([key, entryValue]) => [
        key,
        obfuscateParameterValues(entryValue),
      ])
    );
  }

  return "***";
}
