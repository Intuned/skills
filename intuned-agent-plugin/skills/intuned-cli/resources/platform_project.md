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
  - Get detailed information about a specific project, including whether self-healing is enabled.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON. Includes `self_healing: { enabled: true | false }`.

- `intuned platform self-healing set <level> [options]`:
  - Set the self-healing level for a project. Available levels: `off`, `monitor`, `auto-fix`, `auto-merge`, `auto-deploy`. `auto-fix`, `auto-merge`, and `auto-deploy` require a Hosted project (Connected/CLI projects can only use `off` or `monitor`).
  - Prompts for confirmation before applying. Use `-y` / `--yes` to skip.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-y, --yes`: Skip confirmation prompt.
    - `--json`: Output as JSON.
