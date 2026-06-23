## intuned platform issues

Manage project issues. Use these commands to list, inspect, and dismiss issues detected on the platform for a deployed project.

- `intuned platform issues get <issue-ref> [options]`:
  - Get detailed information about a specific issue by its ID.
  - `<issue-ref>`: The ID of the issue.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intuned platform issues list [options]`:
  - List issues for a project. Supports pagination and filtering.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-l, --limit <number>`: Maximum number of items to return (default: 50).
    - `-o, --offset <number>`: Number of items to skip (default: 0).
    - `--json`: Output as JSON.
  - Useful for finding active issues or reviewing issue history across a project.

- `intuned platform issues dismiss <issue-refs...> [options]`:
  - Mark one or more issues as dismissed — removes them from the open list. Accepts one or more refs, e.g. `Issue-5` or `5`.
  - `<issue-refs...>`: One or more issue references to dismiss.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json [filename]`: Output as JSON; if a filename is given, write the results to that file.
  - **Dismissing is not a fix** — if the underlying problem persists, monitoring re-raises the issue on subsequent job runs. Deploy the actual fix first.
