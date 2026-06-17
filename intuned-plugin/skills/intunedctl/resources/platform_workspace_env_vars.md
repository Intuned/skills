## intuned platform workspace env-vars

Manage **workspace-scoped** environment variables on the Intuned platform. These vars are available across all projects in the workspace, unlike `platform env-vars` which is scoped to a single project.

If a project-level env var and a workspace-level env var share the same key, the project-level one takes precedence within that project.

### Environments

`--envs` accepts a comma-separated list of `AUTHORING`,`PUBLISHED`. Default is `PUBLISHED`. Same semantics as project env vars.

### `intuned platform workspace env-vars list [options]`

List all workspace env vars.

- `-l, --limit <n>` / `-o, --offset <n>`: pagination.
- `--json`.

### `intuned platform workspace env-vars get <key> [options]`

Get a single workspace env var by key.

- `<key>` (required).
- `--json`.

### `intuned platform workspace env-vars create [options]`

Create a new workspace env var.

- `--key <key>` (required): 1–100 chars, alphanumeric or underscore, cannot start with a digit.
- `--value <value>` (required): 1–1000 chars.
- `--description <desc>`: up to 1000 chars.
- `--envs <envs>` (default `PUBLISHED`).
- `--json`.

### `intuned platform workspace env-vars update <current-key> [options]`

Update by current key. Flags omitted are left unchanged.

- `<current-key>` (required).
- `--key`, `--value`, `--description`, `--envs`: as above.
- `--json`.

### `intuned platform workspace env-vars delete <key> [options]`

Delete by key.

- `<key>` (required).
- `--force`: skip confirmation.
- `--json`.

### When to use

Workspace env vars are typically configured by the workspace owner once and reused across projects (shared API keys, common service credentials, etc.). Project env vars override them per project.

You generally do not need to manage workspace env vars yourself — read them with `list`/`get` if you need to check whether a key is already defined workspace-wide before creating a project-level duplicate.
