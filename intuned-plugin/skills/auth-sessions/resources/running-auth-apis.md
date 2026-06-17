# Running Auth sessions APIs

Auth session APIs (`create` and `check`) are not called directly — they run through `intunedctl` commands that manage the full lifecycle: running the code, capturing browser state, saving it, and validating it. The credentials are read from `.parameters/auth-sessions/create/default.json`, which the user fills in directly — you write the file with empty placeholder fields and ask them to enter the values there, never in chat, and you never read it back (see `first-time-authentication.md`). Always use `intunedctl` commands for this — do not run the files directly.

## CLI Commands

All commands support `--cdp-browser-name default` to run against the agent's live browser. **Always use this flag** when working interactively.

Use the Bash tool to run the command and set the `timeout` to at least `600000` (10 min). If it exits with code `143`, call `extendTimeout` inside the API code and increase the Bash `timeout`.

| Command                                                                                     | Description                       |
| ------------------------------------------------------------------------------------------- | --------------------------------- |
| `intunedctl dev attempt authsession create <params> --id <id> --cdp-browser-name default`   | Login flow + verify. Saves state. |
| `intunedctl dev attempt authsession check <id> --cdp-browser-name default`                  | Single check attempt. No retries. |
| `intunedctl dev attempt api <name> <params> --auth-session <id> --cdp-browser-name default` | Run API with auth state injected. |

`<params>` is a JSON string or path to a JSON file (e.g., `.parameters/auth-sessions/create/default.json`).

## Testing Auth Sessions

**Always use `intunedctl` commands to test auth session APIs — do not run the files directly.**

All commands support `--cdp-tab-id <tab_id>` to run on your assigned tab.

### How testing differs from regular APIs

Auth session testing replaces the standard "create parameter files → test every case" workflow:

- **Do NOT create `.parameters/api/` test files.** Auth sessions don't use them. Credentials are already at `.parameters/auth-sessions/create/default.json`.
- **There is one test flow** — run create, then validate. Not "every parameter file."
- **Report the auth session ID** (the credential file name without `.json`, e.g. `default`) on completion so it can be used by other APIs with `--auth-session <id>`.

### Commands

After `create` and `check` are implemented:

```bash
# 1. Create — runs create authsession API and saves the auth-session.
export MODE=generate_code && intunedctl dev attempt authsession create .parameters/auth-sessions/create/default.json --id <auth-session-id> --cdp-browser-name default --cdp-tab-id <tab_id>

# 2. Check - Runs the Check API.
export MODE=generate_code && intunedctl dev attempt authsession check <auth-session-id> --cdp-browser-name default --cdp-tab-id <tab_id>
```

## Running APIs with Auth

```bash
export MODE=generate_code && intunedctl dev attempt api <api-name> .parameters/api/<api-name>/default.json \
  --auth-session <auth-session-id> \
  --cdp-browser-name default \
  --cdp-tab-id <tab_id>
```
