## intunedctl platform env-vars

Manage **project-scoped** environment variables on the Intuned platform. These vars are available to APIs that run within this specific project.

For workspace-wide variables shared across all projects, see `platform_workspace_env_vars.md`.

### Environments

The `--envs` flag controls where the variable is exposed. Supported values are `AUTHORING` and `PUBLISHED` (comma-separated). Default is `PUBLISHED`.

- `AUTHORING`: variable is available in the authoring environment (during dev / agent / IDE work).
- `PUBLISHED`: variable is available in deployed (production) runs.

### `intunedctl platform env-vars list [options]`

List all project env vars.

- `-p, --project-name <name>`: project name (see Project Name Resolution in the docs). Optional — falls back to current context.
- `-l, --limit <n>` / `-o, --offset <n>`: pagination.
- `--json`.

### `intunedctl platform env-vars get <key> [options]`

Get a single env var by key.

- `<key>`: required.
- `-p, --project-name <name>`: optional.
- `--json`.

### `intunedctl platform env-vars create [options]`

Create a new project env var.

- `--key <key>` (required): 1–100 chars, alphanumeric or underscore, cannot start with a digit.
- `--value <value>` (required): 1–1000 chars.
- `--description <desc>`: up to 1000 chars.
- `--envs <envs>` (default `PUBLISHED`): comma-separated `AUTHORING`,`PUBLISHED`.
- `-p, --project-name <name>`: optional.
- `--json`.

### `intunedctl platform env-vars update <current-key> [options]`

Update an existing env var by its current key. Any flag you omit is left unchanged.

- `<current-key>` (required).
- `--key <key>`: rename.
- `--value <value>`: new value.
- `--description <desc>`: new description.
- `--envs <envs>`: replace the env list.
- `-p, --project-name <name>`: optional.
- `--json`.

### `intunedctl platform env-vars delete <key> [options]`

Delete an env var by key.

- `<key>` (required).
- `--force`: skip confirmation prompt.
- `-p, --project-name <name>`: optional.
- `--json`.

### Collecting and storing env vars

For the full decision (which store to use, the AUTHORING/PUBLISHED rule, resolution order), load the **`manage-env-vars`** skill. In brief:

- **Don't put secret values through the agent.** Hand the user the command to run with a `<value>` placeholder — `intunedctl platform env-vars create --key KEY --value <value> ...` (project-level) or `platform workspace env-vars create ...` (workspace-level) — and they fill the value and run it. For local-only, ask them to add `KEY=<value>` to `.env`. Never paste the value into chat or run the command yourself with the secret.
- **A platform var is only available to local `dev attempt`/`dev run` if it includes `--envs AUTHORING`** — the default (`PUBLISHED`) is deployed-only. Default to `--envs AUTHORING,PUBLISHED` so the value works both locally and after deploy.
- Before collecting a new value, consider running `platform workspace env-vars list` — if the key already exists at workspace level, it's inherited by every project (project-level overrides it per project).
