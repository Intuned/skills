## intuned platform attempts

Manage run attempts. Use these commands to inspect individual attempts within a run, download their logs, and retrieve Playwright traces for debugging.

- `intuned platform attempts get <run-id> [attempt-number] [options]`:
  - Get detailed information about a specific attempt within a run.
  - `<run-id>`: The ID of the run.
  - `[attempt-number]`: Optional attempt number. If omitted, returns the latest attempt.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intuned platform attempts log <run-id> [attempt-number] [options]`:
  - Download logs for a specific attempt. Logs are saved as `.jsonl` files.
  - `<run-id>`: The ID of the run.
  - `[attempt-number]`: Optional attempt number. If omitted, returns the latest attempt.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-o, --output-file <path>`: Output file path (default: `log_<run-id>_<attempt-number>.jsonl`).

- `intuned platform attempts trace <run-id> [attempt-number] [options]`:
  - Download the Playwright trace for a specific attempt. Traces are saved as `.zip` files that can be analyzed with the `trace-debugging` skill.
  - `<run-id>`: The ID of the run.
  - `[attempt-number]`: Optional attempt number. If omitted, returns the latest attempt.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-o, --output-file <path>`: Output file path (default: `trace_<run-id>_<attempt-number>.zip`).
