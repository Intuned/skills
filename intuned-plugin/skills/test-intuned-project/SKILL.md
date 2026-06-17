---
name: test-intuned-project
description: "Run and monitor a platform end-to-end test job for Intuned APIs. Use to validate the full chained run on the platform — when the user mentions a platform test, test job, or e2e test."
---

# Types of testing

## Local Testing

Local testing is simply running the API locally with `intunedctl dev attempt api <name> <parameters path> [--auth-session]` or `intunedctl dev run api <name> <parameters path> [--auth-session]`

It also includes running the Auth-session APIs:

```bash
intunedctl dev attempt authsession <name> <parameters path> [--id]
```

These will run the APIs on a local browser. The user can see the API executing in action, you can run with headless or headful browsers.

When running an API locally, make sure to pass a timeout to the bash tool, and pass reasonable parameters, for example, if the API is lopping over pages, and theres a max_pages parameter configured, pass a reasnoble value for local runs, e.g: `{"max_pages":"5"}`, because it may take long time to execute.

The results of the API will be written to an output file, Read it and analyse it, debug errors or unexpected results by using a browser and reproducing the API on the browser instance.

## End-to-end Testing

End-to-end testing includes running the whole API with the extended payloads on Intuned's platform, this means that the APIs will run cloud browsers, it takes longer than local runs since it will run the API and its extended APIs all at once.

You must always confirm with the user before running E2E tests.

# E2E: Test Intuned Project

This is the capability of running and monitoring an Intuned **test job** end-to-end with `intunedctl dev test-job`: trigger it, poll until terminal, download the JSONL results, and diagnose any failures. Test jobs are ephemeral platform executions that simulate actual E2E job execution for validating your code — they run the project's code from the current directory in the cloud, without a real deploy. They are **not** platform Jobs: they never appear on the platform `jobs` list, produce no persistent JobRun, and exist only to verify APIs and job configs end-to-end. Results download as local artifact files under `.intuned-agent/`.

> Unlike local `dev attempt` (which mocks uploads under `MODE=generate_code`), a test job runs in the cloud with **real** attachment uploads to managed S3 — so it's where real attachment results get validated. This requires the project to be provisioned.

## Steps

### 1. Trigger Test Job

**Always check the `intuned-resources/jobs/` directory first.** The `.job.json` files there are the source of truth for what gets tested — they already contain the correct `apiName` and `parameters`.

```bash
ls intuned-resources/jobs/
```

#### Pre-flight: Validate API names and payload keys

Before triggering, verify two things. Both failures are silent — the test runs but the extended call never fires, or you get an "API not found" error at runtime.

1. **Correct key per context** — `extend_payload` / `extendPayload` calls use the key `"api"`; `*.job.json` payload arrays use `"apiName"`. These are not interchangeable.
   - ✅ `extend_payload({"api": "get-details", "parameters": {...}})`
   - ❌ `extend_payload({"apiName": "get-details", ...})` — silently ignored
   - ✅ `*.job.json`: `{ "apiName": "get-details", "parameters": {...} }`
   - ❌ `*.job.json`: `{ "api": "get-details", ... }` — rejected
2. **Name matches a file** — every `"api"` in `extend_payload` calls and every `"apiName"` in job configs must exactly match a filename in `api/` (without the extension).

Fix any mismatches before proceeding.

---

**If `intuned-resources/jobs/` contains `.job.json` files**: Read the `job.json` file and ensure it has correct APIs and parameters. Then trigger one test job per file:

```bash
intunedctl dev test-job trigger --from-job-config intuned-resources/jobs/<name>.job.json --max-runs <n> --json
```

**If no `intuned-resources/jobs/` directory or no `.job.json` files exist**, fall back to inline payloads using the API names and parameters from `.parameters/`:

```bash
intunedctl dev test-job trigger '[{"apiName":"<api-name>","parameters":{}}]' --max-runs <n> --json
```

#### Picking `--max-runs`

Always pass `--max-runs`. The test job stops once that many runs have completed, so you're sampling rather than running to completion.

Jobs with `extend_payload` chains can fan out to hundreds or thousands of runs (e.g. a `list` API producing 500 extended payloads = 501 runs), and each run costs time and credits. If you don't pass `--max-runs`, the poll loop will wait for all of them to finish — which can take hours and eat a lot of credits before you get a result back.

A small sample that exercises the parent and a handful of chained children is usually enough to catch broken selectors, chaining bugs, and output-shape regressions. **15** is a reasonable starting point for a typical chained project — 1 parent plus ~14 children is enough to see the chain working and spot-check output shape. Larger samples give more confidence; smaller samples give a faster feedback loop while iterating on a fix.

#### Auth-Enabled Projects

When `authSessions.enabled` is `true` in `Intuned.json`, you **must** pass `--auth-session-input` with the path to the credentials file, **Do NOT read that file, it has sensitive data** — pass the path only so the values never enter your context:

```bash
intunedctl dev test-job trigger --from-job-config intuned-resources/jobs/<name>.job.json --auth-session-input .parameters/auth-sessions/create/default.json --json
```

**Response**:

```json
{ "status": "pending", "runId": "..." }
```

Save the `runId` for next steps.

### 2. Monitor the Test Job

After triggering, poll the test job until it reaches a terminal state, then move on to analysis.

#### Polling

Poll the test job status using `--wait-for 4m` to block for up to 4 minutes per poll:

```bash
intunedctl dev test-job result <runId> --quiet --wait-for 4m --json
```

For this polling loop, always use `--wait-for 4m`. Set the Bash tool timeout to `300000` (5 minutes) so the command isn't killed mid-wait. **Never use `sleep` or `timeout`** — the `--wait-for` flag handles the waiting.

While the test job is pending, the response includes a `progress` object. The counts refer to runs (one per API execution):

```json
{
  "status": "pending",
  "runId": "...",
  "progress": {
    "pending": 3,
    "running": 2,
    "completed": 5,
    "succeeded": 4,
    "failed": 1,
    "cancelled": 0
  }
}
```

While `pending`, poll again — test jobs with many runs can take a long time, so a job showing `pending` for a while is normal. On a terminal response, read the top-level `status`:

- `status: "succeeded"` — the sample completed. When `--max-runs` was set, any extra payloads that would have exceeded the cap show up as cancelled runs in the downloaded JSONL with `reason.type: "terminated"` and a message starting with `Max runs exceeded`. This is the normal capped outcome. Proceed to Step 3.
- `status: "terminated"` — the job was terminated externally. Note the external termination and investigate what you have (Step 3).
- `status: "failed"` — platform-level failure (not an API failure). Do not download; follow **Handling Failures** below.

For any non-`failed` terminal status, proceed to Step 3 (Analyze), then Step 4/5 (Download / Debug). Use the diagnostics to fix any code, then re-trigger a test job and poll again to verify.

**If progress stalls**: if the progress numbers haven't changed for several consecutive polls, stop waiting. Decide whether to keep polling, or terminate the test job with `intunedctl dev test-job terminate <runId>` and re-trigger after investigating. Don't loop forever on a stalled job.

**Handling Failures**:

If the result returns with `"status": "failed"`:

```json
{
  "status": "failed",
  "runId": "..."
}
```

This indicates a platform-level failure (not an API execution failure). In this case:

1. **Retry once after a delay**: Wait for few seconds, then re-trigger a new test job with the same parameters
2. **If it fails again**: Stop and report to the user:

   > "The platform test job failed twice. This indicates an issue with Intuned's platform. Please contact the Intuned team for support."

Do not continue with further debugging or retry attempts - this is a platform infrastructure issue, not a code issue.

### 3. Analyze Results

**Result structure**:

```json
{
  "status": "succeeded",
  "runId": "...",
  "result": {
    "summary": { "successful_runs": 1, "failed_runs": 0, "error": null },
    "aggregate": { "signed_url": "...", "format": "jsonl" }
  }
}
```

**Interpreting run counts with `extend_payload`**:

Load the `intuned-overview` skill to understand how APIs chain via `extend_payload` and relate to each other.

| Result         | Meaning                                  |
| -------------- | ---------------------------------------- |
| All failed     | Parent API (e.g., `list.py`) failed      |
| All successful | All APIs executed correctly              |
| Mixed          | Parent succeeded, some child runs failed |

Example: `list.py` extends to `details.py` → 10 successful + 3 failed means `list.py` worked, 3 of 13 `details.py` runs failed.

### 4. Download Results

```bash
mkdir -p .intuned-agent/test_runs/<run_id>/<api-name>
intunedctl dev test-job download <run_id> --quiet
```

The result file is a jsonl File that contains each run's result.
eg, if a single API ran, it will contian 1 json line for its results and 0 appended payloads
If it had appended payloads, and it ran these extended payloads, it will contain multiple Json lines for each API run result.

### 5. Debug Runs

Each line in the results.jsonl file represents one API run. Results can be successful or failed.

#### Successful Run

```json
{
  "apiInfo": {
    "name": "<API_NAME>",
    "parameters": { <API_PARAMS> },
    "runId": "abc-123",
    "result": {
      "output": {
        <API_RESULT>
      },
      "extendedPayloads": [EXTENDED_PAYLOADS]
    },
    "started_at": "..",
    "ended_at": "...",
    "error": null,
    "reason": null,
    "trace_url": "<PLAYWRIGHT TRACE DOWNLOAD URL>",
    "log_url": "<LOGS DOWNLOAD URL>"
  },
  "workspaceId": "...",
  "project": {...},
  "projectJob": {...},
  "projectJobRun": {...}
}
```

Key: `error` is `null` and `result` contains output data.

#### Failed Run

```json
{
  "apiInfo": {
    "name": "<API_NAME>",
    "parameters": {<PARAMETERS>},
    "runId": "...",
    "result": null,
    "started_at": "...",
    "ended_at": "...",
    "error": {
      "message": "Error Message",
      "code": "ERROR CODE",
      "category": "ERROR CATEGORY",
      "doc_url": "INTUNED DOCS FOR ERROR CODES",
      "details": {
        "attempts_count": ..
      }
    },
    "reason": null,
    "trace_url": "<PLAYWRIGHT TRACE DOWNLOAD URL>",
    "log_url": "<LOGS DOWNLOAD URL>"
  },
  "workspaceId": "...",
  "project": {...},
  "projectJob": {...},
  "projectJobRun": {...}
}
```

Use `jq`, `awk`, `grep` and other useful commands to help you extract runs effectively.

**Identifying APIs that extend other APIs**: If a run has `extendedPayloads` in its result, this API triggered child API runs. Each entry specifies the child API name and the parameters passed to it:

```json
"extendedPayloads": [
  {
    "api": "<CHILD_API_NAME>",
    "parameters": {
      "<param_1>": "<extracted_value_1>",
      "<param_2>": "<extracted_value_2>",
      "<detail_url_param>": "<URL_TO_DETAIL_PAGE>",
      "<unique_id_param>": "<UNIQUE_IDENTIFIER>"
    }
  }
]
```

**Filter failed runs and extract error details:**

```bash
jq -c 'select(.apiInfo.error) | {api: .apiInfo.name, runId: .apiInfo.runId, error: .apiInfo.error.message, code: .apiInfo.error.code, parameters: .apiInfo.parameters}' result.jsonl
```

**Filter successful runs:**

```bash
jq -c 'select(.apiInfo.error == null) | {api: .apiInfo.name, runId: .apiInfo.runId, parameters: .apiInfo.parameters}' result.jsonl
```

**Count failed vs successful:**

```bash
jq -c 'select(.apiInfo.error)' result.jsonl | wc -l
jq -c 'select(.apiInfo.error == null)' result.jsonl | wc -l
```

**Count and inspect extended payloads:**

```bash
# Count extended payloads from the parent API run
jq -c 'select(.apiInfo.result.extendedPayloads | length > 0) | {api: .apiInfo.name, extended_count: (.apiInfo.result.extendedPayloads | length), child_api: .apiInfo.result.extendedPayloads[0].api}' result.jsonl

# List all extended payloads with their parameters
jq -c 'select(.apiInfo.result.extendedPayloads | length > 0) | .apiInfo.result.extendedPayloads[]' result.jsonl

# First and last extended payload (for spot-checking)
jq -c 'select(.apiInfo.result.extendedPayloads | length > 0) | .apiInfo.result.extendedPayloads[0]' result.jsonl
jq -c 'select(.apiInfo.result.extendedPayloads | length > 0) | .apiInfo.result.extendedPayloads[-1]' result.jsonl
```

**Get extraction output keys and spot-check values:**

```bash
# Get the keys of the output object from the first successful run
jq -c 'select(.apiInfo.error == null) | .apiInfo.result.output | keys' result.jsonl | head -1

# Show keys with their values for a quick scan (first successful run)
jq -c 'select(.apiInfo.error == null) | .apiInfo.result.output' result.jsonl | head -1
```

Cross-reference the output keys against the API source code. Every field the API is supposed to extract must appear in the output. If a field exists as a key but has an empty string `""` or `null` as its value, the selector for that field is broken or not extracting properly.

#### Debugging Failed Runs

For each failed run, download and analyze both the Playwright trace and the logs file to understand the root cause before attempting any fix.

**1. Download the Playwright trace:**

Each failed run includes a `trace_url` field. Download the trace file:

```bash
curl -L "<trace_url>" -o .intuned-agent/test_runs/<Test_RunUd>/<Specific_RunId>/<api-name>/trace.zip
```

**2. Debug with trace-debugging skill:**

Load the `trace-debugging` skill to understand how to debug and analyze the trace. You will understand what happened, what failed and what went wrong.

**3. Download and inspect the logs:**

Each failed run also includes a `log_url` which is a jsonl file containing all the logs. Download and read the logs:

```bash
curl -L "<log_url>" -o .intuned-agent/test_runs/<Test_RunUd>/<Specific_RunId>/<api-name>/logs.jsonl
```

Read the logs to understand the full execution context - error stack traces, timing information, and any warnings that preceded the failure.
Each json line is an object of the timestamp and the log message

**4. Combine insights and fix:**

Use the combined information from the trace analysis, logs, and error message to:

- Understand the root cause of the failure
- Reproduce the issue locally by running the API with the same parameters that failed
- Fix the failing API code
- Re-run the test to verify the fix

We want a completely working API, without errors.
All extended Payloads should work without errors and return results as expected.

## Quick Reference

| Command                                                                                                          | Purpose                       |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `intunedctl dev test-job trigger --from-job-config intuned-resources/jobs/<name>.job.json --max-runs <n> --json` | Start test (from jobs/)       |
| `intunedctl dev test-job trigger '[{"apiName":"..."}]' --max-runs <n> --json`                                    | Start test (inline, fallback) |
| `intunedctl dev test-job result <runId> --quiet --wait-for 4m --json`                                            | Poll status (blocks up to 4m) |
| `intunedctl dev test-job download <run_id> --quiet`                                                              | Download results              |
| `intunedctl dev test-job terminate <run_id> --json`                                                              | Terminate a running test      |

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
