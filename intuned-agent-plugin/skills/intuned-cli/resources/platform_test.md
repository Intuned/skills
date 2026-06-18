## intuned dev test-job

Run and manage test executions. Use these commands to trigger test runs using code from the current directory, check test results, and download them.
This is useful to perform an End to End test for an API on Intuned's platform.

- `intuned dev test-job trigger [payloads] [options]`:
  - Trigger a new test run with code from the current directory. This uploads the local project code and runs it as a test on the platform.
  - Two modes:
    - **Job config mode**: `--from-job-config <path>` — loads `payload` and `configuration` from a `.job.json` file.
    - **Inline mode**: positional `[payloads]` — inline JSON array or path to a JSON file containing a payloads array, with configuration via individual flags.
  - Options:
    - `--from-job-config <path>`: Job config file path (payload + configuration). Mutually exclusive with positional payloads.
    - `--auth-session-input <path>`: Path to JSON file with auth session input.
    - `--max-concurrent-requests <n>`: Max concurrent requests (inline mode).
    - `--retries <n>`: Max retry attempts per payload (inline mode).
    - `--request-timeout <n>`: Request timeout in seconds (inline mode).
    - `--max-runs <n>`: Stop the test job once `n` runs have completed.
    - `-q, --quiet`: Suppress progress messages.
    - `--json`: Output as JSON.

- `intuned dev test-job result <run-id> [options]`:
  - Get the result of a test run.
  - `<run-id>`: The ID of the test run.
  - Options:
    - `-q, --quiet`: Suppress progress messages.
    - `--json`: Output as JSON.
    - `-w, --wait-for <duration>`: Wait for the test to complete before returning results. Accepts durations like `'30s'`, `'5m'`.

- `intuned dev test-job download <run-id> [options]`:
  - Download test results to a file.
  - `<run-id>`: The ID of the test run.
  - Options:
    - `-q, --quiet`: Suppress progress messages.
    - `-w, --wait-for <duration>`: Wait for the test to complete before downloading. Accepts durations like `'30s'`, `'5m'`.

- `intuned dev test-job terminate <run-id> [options]`:
  - Terminate a running test job. Use when a test run is stalled, no longer needed, or you want to stop it before completion.
  - `<run-id>`: The ID of the test run to terminate.
  - Options:
    - `-q, --quiet`: Suppress progress messages.
    - `--json`: Output as JSON.
  - Returns 202 if termination was initiated, 409 if the run already completed.
