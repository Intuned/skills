## intunedctl platform jobs

Manage automation jobs for a deployed project. Use these commands to create, list, inspect, trigger, update, pause, resume, and delete jobs.

- `intunedctl platform jobs create <data> [options]`:

  - Create a new automation job.
  - `<data>`: Job configuration as an inline JSON string or a path to a JSON file.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

  **Job configuration schema:**

  For complete details on Job configuration schema, use `search_intuned` → `query_docs_filesystem_intuned`.

  **Example — create a job from an inline JSON string:**

  ```bash
  intunedctl platform jobs create '{"id":"my-job","payload":[{"apiName":"get-data","parameters":{}}],"configuration":{"retry":{"maximumAttempts":3}},"schedule":{"calendars":[{"hour":12,"minute":51,"dayOfWeek":["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"]}],"jitter":"6h"}}'
  ```

  **Example — create a job from a file:**

  ```bash
  intunedctl platform jobs create jobs/my-job.job.json
  ```

- `intunedctl platform jobs list [options]`:

  - List jobs for a project. Supports pagination.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-l, --limit <number>`: Maximum number of items to return (default: 50).
    - `-o, --offset <number>`: Number of items to skip (default: 0).
    - `--json`: Output as JSON.

- `intunedctl platform jobs get <job-id> [options]`:

  - Get detailed information about a specific job.
  - `<job-id>`: The ID of the job.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intunedctl platform jobs trigger <job-id> [options]`:

  - Manually trigger a job run.
  - `<job-id>`: The ID of the job to trigger.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intunedctl platform jobs update <job-id> <data> [options]`:

  - Update an existing automation job. **API-origin Jobs only.** For Code-origin Jobs, edit the `*.job.json` file and redeploy with `intunedctl dev deploy`.
  - `<job-id>`: The ID of the job to update.
  - `<data>`: New job configuration as an inline JSON string or a path to a JSON file (same shape as `create`).
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

  **Examples:**

  ```bash
  intunedctl platform jobs update my-job ./jobs/my-job.job.json
  intunedctl platform jobs update my-job '{"configuration":{"retry":{"maximumAttempts":5}}}'
  ```

- `intunedctl platform jobs pause <job-id> [options]`:

  - Pause a job. Scheduled runs stop firing until the job is resumed. **Works on both Code-origin and API-origin Jobs** (operational toggle, not an edit).
  - `<job-id>`: The ID of the job to pause.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intunedctl platform jobs resume <job-id> [options]`:

  - Resume a paused job. Scheduled runs fire again per the job's schedule. **Works on both Code-origin and API-origin Jobs** (operational toggle, not an edit).
  - `<job-id>`: The ID of the job to resume.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intunedctl platform jobs delete <job-id> [options]`:

  - Delete a job. **API-origin Jobs only.** For Code-origin Jobs, remove the `*.job.json` file and redeploy with `intunedctl dev deploy`. Asks for an interactive confirmation prompt before deleting; pass `-y` / `--yes` to skip.
  - `<job-id>`: The ID of the job to delete.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-y, --yes`: Skip the confirmation prompt.
    - `--json`: Output as JSON.
