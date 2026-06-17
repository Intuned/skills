## intunedctl platform runs

Manage automation runs. Use these commands to list, inspect, and start runs for a deployed project.

- `intunedctl platform runs get <run-id> [options]`:
  - Get detailed information about a specific run by its ID.
  - `<run-id>`: The ID of the run.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intunedctl platform runs list [options]`:
  - List runs for a project. Supports pagination and filtering.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-l, --limit <number>`: Maximum number of items to return (default: 50).
    - `-o, --offset <number>`: Number of items to skip (default: 0).
    - `--json`: Output as JSON.
    - `-f, --filter <filter...>`: Filter expression. Examples: `"status=FAILED"`, `"run_duration>5000"`.
  - Useful for finding failed runs or analyzing run history.

- `intunedctl platform runs start <data> [options]`:
  - Start a new automation run.
  - `<data>`: Run configuration data (JSON or path to JSON file).
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.
