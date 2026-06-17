## intuned platform project

Manage and inspect projects on the Intuned platform.

- `intuned platform project list [options]`:
  - List all projects in the workspace.
  - Options:
    - `--limit <number>`: Maximum number of projects to return (default: 50).
    - `--offset <number>`: Skip the first N projects (default: 0).
    - `--ai-enabled`: Only show projects with AI enabled (agent_level >= 1).
    - `--json`: Output as JSON. Returns `[{ "name": "...", "language": "TypeScript" | "Python" }]`.

- `intuned platform project get [options]`:
  - Get detailed information about a specific project.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.
