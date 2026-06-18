## intuned platform issues

Manage project issues. Use these commands to list and inspect issues detected on the platform for a deployed project.

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
