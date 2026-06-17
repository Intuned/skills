## intuned platform jobruns

Manage job runs. Use these commands to list, inspect, and terminate individual job runs.

- `intuned platform jobruns list <job-id> [options]`:
  - List job runs for a specific job. Supports pagination.
  - `<job-id>`: The ID of the job.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-l, --limit <number>`: Maximum number of items to return (default: 50).
    - `-o, --offset <number>`: Number of items to skip (default: 0).
    - `--json`: Output as JSON.

- `intuned platform jobruns get <job-run-id> [options]`:
  - Get detailed information about a specific job run. The owning job is resolved automatically from the run ID.
  - `<job-run-id>`: The ID of the job run.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intuned platform jobruns terminate <job-run-id> [options]`:
  - Terminate a job run that is still in flight. The owning job is resolved automatically from the run ID. No-op for runs that have already reached a terminal state.
  - `<job-run-id>`: The ID of the job run to terminate.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.
