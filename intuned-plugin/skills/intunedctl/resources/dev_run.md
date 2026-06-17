## intuned dev run

`dev run` executes a full Run (with retry logic) locally. Use it when you want to mirror production behavior end-to-end. For a single attempt without retries, use `intuned dev attempt` instead.

### `intuned dev run api <api-name> <parameters> [options]`

Execute an API run locally.

- `<api-name>`: Name of the API (path under `api/`, no extension; use `/` for nested dirs).
- `<parameters>`: Inline JSON or path to a JSON file (commonly `.parameters/api/<api-name>/<name>.json`).

Common options:

- `--retries <n>` (default 1): retries on failure during the API execution.
- `--auth-session <id>`: required if auth sessions are enabled in `Intuned.json`. Files are expected at `./auth-sessions-instances/<id>`.
- `--auto-recreate`: re-create the auth session if validation fails.
- `--auth-check-retries <n>` / `--auth-create-retries <n>`: retry counts for auth check/create paths.
- `-o, --output-file <path>`: write the run result (and extended payloads) to a JSON file instead of stdout.
- `--proxy <url>`, `--headless`, `--trace`, `--traces-path <path>`, `--timeout <time>`, `--start-to-end-timeout <time>`, `--keep-browser-open`, `--cdp-url <url>`, `--cdp-browser-name <name>`, `--cdp-tab-id <id>`.

### `intuned dev run authsession create <parameters> [options]`

Run a full AuthSession:Create. Auth sessions must be enabled in `Intuned.json`.

- `<parameters>`: Inline JSON or path to a JSON file.
- `--id <id>`: ID of the auth session to create (default `auth-session-{timestamp}`). Files end up in `./auth-sessions-instances/<id>`.
- `--check-retries <n>` / `--create-retries <n>`: retry counts for the post-create validity check and the create step itself.
- Shared options: `--proxy`, `--timeout`, `--start-to-end-timeout`, `--headless`, `--trace`, `--traces-path`, `--auth-session-instances-path`, `--keep-browser-open`, `--cdp-url`, `--cdp-browser-name`, `--cdp-tab-id`.

### `intuned dev run authsession validate <id> [options]`

Run a full AuthSession:Validate against an existing session.

- `<id>`: auth session ID under `./auth-sessions-instances/<id>`.
- `--auto-recreate`: recreate the session if validation fails.
- `--check-retries <n>` / `--create-retries <n>`: retry counts (create-retries only applies if `--auto-recreate` is set).
- Shared options as above.

### `intuned dev run authsession update <id> [options]`

Run a full AuthSession:Update on an existing session.

- `<id>`: auth session ID under `./auth-sessions-instances/<id>`.
- `--input <parameters>`: new JSON parameters (inline or file path). If omitted, the last used parameters are reused.
- `--check-retries <n>` / `--create-retries <n>`.
- Shared options as above.

### `dev run` vs `dev attempt`

- `dev run` follows the configured retry logic and is closest to production behavior. Use it for end-to-end checks or when reproducing flakes.
- `dev attempt` runs once with no retries — faster and easier to debug. Prefer it during iterative development.
