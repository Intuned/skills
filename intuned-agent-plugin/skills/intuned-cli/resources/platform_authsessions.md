## intuned platform authsessions

Manage platform auth sessions for a deployed project. Use these commands to create, inspect, validate, update, and delete auth sessions on the Intuned platform.

**Prerequisite**: Auth sessions must be enabled in the project settings (`authSessions.enabled: true` in `Intuned.json`). All commands fail fast if the project is not found or auth sessions are not enabled.

---

- `intuned platform authsessions list [options]`:
  - List all auth sessions for a project.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `-l, --limit <number>`: Maximum number of items to return (default: 50).
    - `-o, --offset <number>`: Number of items to skip (default: 0).
    - `-f, --filter <filter...>`: Filter expression. Filterable fields: `state` (enum), `type` (enum), `id` (string), `created_at` (date). Example: `"state=READY"`.
    - `--json`: Output as JSON.
  - Session states: `READY` (valid), `PENDING` (being created/updated), `EXPIRED` (invalid, needs recreation).

- `intuned platform authsessions get <auth-session-id> [options]`:
  - Get detailed information about a specific auth session.
  - `<auth-session-id>`: The ID of the auth session.
  - Returns: `id`, `state`, `type`, `environment`, `created_at`, `updated_at`, `proxy`.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

- `intuned platform authsessions create <auth-session-id> [options]`:
  - Create a new auth session on the platform. Triggers the `auth-sessions/create` API with the provided credentials.
  - `<auth-session-id>`: The ID to assign to the new auth session (e.g. `default`, `admin`).
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--input <json-or-file>`: Credentials parameters as a JSON string or `@/path/to/file.json`. **Always use the `@file` form** (e.g. `@.parameters/auth-sessions/create/default.json`) — never pass credential values inline.
    - `--proxy <url>`: Proxy URL to use for this session.
    - `--wait [duration]`: Wait for the operation to complete. Optional duration (e.g. `5m`, `30s`, `2h`). Default when flag is provided without a value: `10m`. Without this flag, returns immediately with `operationId`.
    - `--json`: Output as JSON.
  - Use `--wait` when you need to confirm the session was created successfully before proceeding.

- `intuned platform authsessions update <auth-session-id> [options]`:
  - Re-run the create flow for an existing auth session (e.g. to refresh credentials or fix an expired session).
  - `<auth-session-id>`: The ID of the auth session to update.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--input <json-or-file>`: New credentials parameters as a JSON string or `@/path/to/file.json`. **Always use the `@file` form** — never pass credential values inline.
    - `--proxy <url>`: New proxy URL.
    - `--wait [duration]`: Wait for completion. Same behavior as `create --wait`.
    - `--json`: Output as JSON.

- `intuned platform authsessions validate <auth-session-id> [options]`:
  - Validate an existing auth session by running the `auth-sessions/check` API. Always polls until done or timeout.
  - `<auth-session-id>`: The ID of the auth session to validate.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--timeout <seconds>`: Timeout in seconds (default: 300). Throws an error if exceeded.
    - `--json`: Output as JSON.
  - Exits with error if validation fails or times out. Use this to confirm a session is healthy before running APIs.

- `intuned platform authsessions delete <auth-session-id> [options]`:
  - Delete an auth session permanently.
  - `<auth-session-id>`: The ID of the auth session to delete.
  - Options:
    - `-p, --project-name <name>`: Project name (overrides settings file).
    - `--json`: Output as JSON.

---

## Debugging an Auth Session

When investigating a failing auth session on the platform:

```bash
# 1. List all sessions to find the one you're looking for and check its state
intuned platform authsessions list -p <project-name>

# 2. Inspect the specific session
intuned platform authsessions get <auth-session-id> -p <project-name>

# 3. Validate it to confirm whether it's still authenticated
intuned platform authsessions validate <auth-session-id> -p <project-name>

# 4a. If expired/invalid — update (re-run create with existing or new credentials)
intuned platform authsessions update <auth-session-id> -p <project-name> --wait

# 4b. Or delete and recreate with fresh credentials
intuned platform authsessions delete <auth-session-id> -p <project-name>
intuned platform authsessions create <auth-session-id> -p <project-name> --input '{"username":"...","password":"..."}' --wait
```
