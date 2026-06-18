---
name: manage-jobs
description: "Create, edit, and manage Intuned Jobs — the .job.json schema, code-origin vs api-origin handling, name-uniqueness rules, schedules, auth_session, sinks, and intuned platform jobs commands. Load when creating or editing a job config or managing platform jobs."
---

# Manage Jobs

Jobs are blueprints that define when, how, and what browser automations to execute. Instead of triggering individual API runs manually, Jobs let you orchestrate multiple automation executions together — running them in bulk, on a schedule, or both. They handle scheduling, retries, concurrency management, and result aggregation.

```
Job (blueprint)
  └── JobRun (execution instance)
        ├── Run 1 (API execution for payload item 1)
        │     └── Attempt 1, Attempt 2, etc.
        ├── Run 2 (API execution for payload item 2)
        │     └── Attempt 1, Attempt 2, etc.
        └── Run N (API execution for payload item N)
              └── Attempt 1, Attempt 2, etc.
```

Jobs are tightly coupled with the way APIs chain to each other — understand how APIs connect (`extend_payload` and chaining) before composing job payloads. Jobs run on the Intuned Platform and can be controlled via `intuned` cli.

### Jobs vs. test jobs

Don't confuse a **Job** with a **test job** (`intuned dev test-job`, see the `test-intuned-project` skill):

- A **Job** is a persistent platform resource on a **deployed** project. It runs on a schedule or is triggered manually, appears on the platform `jobs` list, and produces persistent JobRuns. This is the real, ongoing automation.
- A **test job** is an ephemeral, one-off execution that runs the current code in the cloud to verify the whole project works **end-to-end before you deploy** — it confirms a real Job would run as expected. It never appears on the `jobs` list and leaves no persistent JobRun.

So: use a **test job** to validate the project during the build; create a **Job** (this skill) for the automation that actually runs on the deployed project.

---

## Job Origin

Every job has an **Origin** that tells you how it was created.

- **Created via API/UI** (raw value `API`) — Created by the user in the Intuned platform UI. No local file exists.
- **Created via Code** (raw value `CODE`) — Backed by a file in `intuned-resources/jobs/`. The file is the source of truth.

---

## Example job configuration

> **Warning:** `apiName` must exactly match the API filename without its extension. For example, `get-product` for `get-product.py` or `get-product.ts`. A mismatch causes "API not found" errors at runtime.

```json
{
  "payload": [
    {
      "apiName": "get-product",
      "parameters": { "url": "https://example.com/product-1" }
    },
    {
      "apiName": "get-product",
      "parameters": { "url": "https://example.com/product-2" }
    }
  ],
  "configuration": {
    "maxConcurrentRequests": 2,
    "retry": { "maximumAttempts": 3 }
  },
  "auth_session": {
    "id": "<auth-session-id>",
    "checkAttempts": 3,
    "createAttempts": 3
  },
  "proxy": "<proxy-url>"
}
```

### `auth_session` field

When the project has auth sessions enabled, every job must include an `auth_session` field so the job can obtain a valid authenticated session before running. Without it the job will fail on protected pages.

| Field            | Type   | Default | Description                                                                                                                                                                               |
| ---------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`             | string | —       | The auth-session ID to use. This is the `<name>` from the corresponding `intuned-resources/auth-sessions/<name>.auth-session.json` file (i.e. the filename without `.auth-session.json`). |
| `checkAttempts`  | number | 3       | How many times the platform checks whether an existing session is still valid before deciding to create a new one.                                                                        |
| `createAttempts` | number | 3       | How many times the platform attempts to create a fresh session if the check fails.                                                                                                        |

**Example** (using a `default` auth session):

```json
{
  "auth_session": {
    "id": "default",
    "checkAttempts": 3,
    "createAttempts": 3
  }
}
```

See the **auth-sessions** skill for how auth sessions are defined and named.

### Schedule field

The schedule field has 2 types: interval & calendars. Useful for user-specific schedule requests.

**Only add a schedule when the user explicitly asks for one.** Do not add a schedule by default.

---

## 1. Create a Job

**NOTE:** Two job origins behave differently:

- **Code-origin** (`intuned-resources/jobs/*.job.json`) — only takes effect after the project is **deployed** (`intuned dev deploy`). If a Code-origin job is configured to run every day at a specific time, it won't actually run until deploy.
- **API-origin** (created via `intuned platform jobs create` or the platform UI on an **already-deployed** project) — takes effect immediately. No further deploy is needed.

There are two ways to create a job for an Intuned project.

### Method A: Local Job File (jobs-as-code) — preferred

**Before writing the file, check for name conflicts.** Job IDs must be unique. Run both checks:

```bash
# Check existing local job files
ls intuned-resources/jobs/

# Check jobs already on the platform (if project is deployed)
intuned platform jobs list --json
```

If a job with the same ID already exists (locally or on the platform), stop and tell the user. Ask them to confirm a different ID or confirm they want to overwrite. Do not silently overwrite.

Create a `intuned-resources/jobs/` directory in the project root and add a `.job.json` file for each job. If the directory already exists, write the job files into it. These files are committed alongside the code and are saved to the Intuned platform once the project is deployed.

```bash
mkdir -p intuned-resources/jobs/
```

Create `intuned-resources/jobs/<job-id>.job.json` with the job configuration.

These local job files are used directly with `intuned dev test-job trigger --from-job-config intuned-resources/jobs/<job-id>.job.json` for E2E testing, and serve as the source of truth for what the job does.

---

### Method B: Via CLI (requires deployed project)

Use this to inspect jobs already created on deployed projects, you can list, get or create new jobs directly on the platform. This does not touch the local file system.

```bash
# List existing jobs on the deployed project
intuned platform jobs list

# Get details of a specific job
intuned platform jobs get <job-id>

# Create a new job on the platform
intuned platform jobs create '<data> [options]'

# or from a file:
intuned platform jobs create intuned-resources/jobs/<job-id>.job.json
```

---

## 2. Edit a Job

Check the job's origin first.

- **Code-origin** → edit the `*.job.json` file in `intuned-resources/jobs/`, then redeploy with `intuned dev deploy`. The platform rejects `intuned platform jobs update | delete` on Code-origin Jobs. `platform jobs pause` and `resume` _do_ work on Code-origin Jobs — fine for one-off operational toggles without a redeploy.
- **API-origin** → there is no local file. Manage via the CLI:

  ```bash
  intuned platform jobs update <job-id> <data>   # data is inline JSON or a path to a JSON file
  intuned platform jobs pause <job-id>
  intuned platform jobs resume <job-id>
  intuned platform jobs delete <job-id>          # asks confirmation; pass -y to skip
  ```

**Workflow:**

1. List job files to find the one to edit:
   ```bash
   ls intuned-resources/jobs/
   ```
2. Read the target file (e.g. `intuned-resources/jobs/my-job.job.json`) to understand its current configuration.
3. Apply the requested change (update payload, schedule, configuration, proxy, etc.).
4. Inform the user that the change will take effect on the next deployment.

---

## 3. Configuring a Sink

Sinks automatically deliver Run results to a destination as each Run completes, instead of requiring polling. Only configure a sink when the user asks for one.

**Always ask the user for the webhook URL and any headers before writing the sink config. Never use a placeholder URL.**

### Webhook Sink

Sends results as a POST request to an HTTP endpoint.

| Field        | Type        | Required | Description                                                  |
| ------------ | ----------- | -------- | ------------------------------------------------------------ |
| `type`       | `"webhook"` | yes      | Sink type                                                    |
| `url`        | string      | yes      | Destination URL (ask the user)                               |
| `headers`    | object      | no       | Headers to include (ask the user)                            |
| `skipOnFail` | boolean     | no       | If `true`, failed Run results are not sent (default `false`) |
| `apisToSend` | string[]    | no       | Limit to specific API names; omit to send all                |

### S3 Sink

If the user asks for an S3 sink, consult the Intuned docs and guide them from there.
