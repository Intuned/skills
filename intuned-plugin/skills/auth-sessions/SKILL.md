---
name: auth-sessions
description: How authentication works in Intuned projects — login flows, auth session APIs, CLI, and calling site backends after auth. Load for login walls, gated content, CSRF/API 403s, or restricted resources.
---

# Auth Sessions

Authentication in Intuned is handled through auth sessions — the capability of logging into a protected site once, preserving that browser state, and reusing it across API runs. A project includes auth sessions only when its target website sits behind a login wall.

> **2FA is not supported.** If you logged in and then the site asks for a 2FA / OTP / TOTP / authenticator code, stop and tell the user to contact `support@intunedhq.com`. Don't ask the user for the code.

## What Auth Sessions Are

Auth sessions preserve browser state (cookies, localStorage, sessionStorage) after a successful login. Two APIs run the lifecycle, placed in special `auth-sessions` directory in the **project root** (not inside `api/`):

- **`auth-sessions/create`** (`.py` or `.ts`) — Login flow. Receives credentials as parameters, logs in, verifies success. Runtime captures browser state afterward.
- **`auth-sessions/check`** (`.py` or `.ts`) — Validation. Loads stored state, navigates to a protected page, returns a boolean indicating whether the session is still valid.

## Auth Session Lifecycle

Intuned manages auth sessions automatically, so API code never handles login itself:

1. **Create** — `create` runs with credentials, logs in, and the runtime captures and saves the browser state.
2. **Run API with auth** — before each run, `check` validates the session; if invalid, `create` recreates it; then the API runs with the authenticated browser state injected automatically.

Auth session APIs are not run like normal APIs — Intuned has dedicated CLI commands for running them and managing their lifecycle. Read `resources/running-auth-apis.md` for the commands.

## Credentials Parameter Files

Credentials are stored as JSON parameter files at `.parameters/auth-sessions/create/{name}.json` (e.g. `default.json`, `admin.json`). Each file contains the key-value pairs for that login and is passed to the `auth-sessions/create` API as input parameters.

To collect credentials, **do NOT ask the user to paste them into the chat — you must never see the secret values.** Instead, write the file yourself with the login form's field names (e.g. `username`/`password`) and **empty placeholder values**, then ask the user to open the file and fill in the real values directly. Example to write:

```json
{ "username": "", "password": "" }
```

Then tell the user the path and ask them to fill it in (not in chat — you won't read it back), and wait for them to confirm before running the auth session. Check the list script first — if a credential file already exists with the right fields, assume it's filled and don't recreate it. Never echo stored secrets back; the same care applies to `auth-sessions-instances/`, which stores browser state.

Run this skill's bundled `scripts/list-credentials.sh` — the path is relative to **this skill's own directory** (resolve it against the skill's base directory shown when the skill loads), and run it with the project root as the working directory:

```bash
scripts/list-credentials.sh
```

Returns credential file names and their field names (e.g. `username`, `password`) without exposing any values.

## Enabling Auth in Intuned.json

Auth sessions are enabled by setting two flags together in `Intuned.json`:

```json
{
  "apiAccess": { "enabled": true },
  "authSessions": { "enabled": true, "type": "API" }
}
```

Both are required together — `type: "API"` is mandatory when `enabled: true`, and `apiAccess` must also be enabled. Once set, **all** API runs require `--auth-session <id>`, even APIs that don't touch login.

## Authenticated backend calls

Auth restores cookies and storage, but **`page.context.request` and similar must match a successful browser request** for that site. Don’t assume one CSRF pattern (e.g. cookie + `X-Requested-With: XMLHttpRequest`) without checking — tokens may live in storage or need different headers.

- **Match a real trace** — DevTools Network or `intuned-agent/tab_${tabId}/network/`: same URL, method, body, and auth headers. User cURL is often incomplete.
- **Debug 403s** — Short read-only **`page.evaluate`** checks on `document.cookie` / `localStorage` / `sessionStorage`. Don’t log secrets.
- **Order** — Open the pages the app needs so tokens exist **before** replaying API calls.

## Resources

Each task has a dedicated resource that holds the exact CLI commands and function signatures — read the relevant one before acting, since guessing produces wrong CLI commands and wrong signatures:

- **First time encountering auth** → `resources/first-time-authentication.md`
- **Auth not set up yet** → add the two flags to `Intuned.json` (above), then follow first-time-authentication if you still need to log in manually
- **Auth set up and browser already authenticated** → proceed normally with automatic authentication using `--auth-session <id>`
- **Running or testing auth session APIs** → `resources/running-auth-apis.md`
- **Implementing `create` or `check`** → the guide for your language:
  - Python: `resources/python/writing-create-and-check-apis.md`
  - TypeScript: `resources/typescript/writing-create-and-check-apis.md`
- **Creating auth-sessions as code `.auth-session.json` resource files** → `resources/auth-sessions-as-code.md`
- **Implementing an API that hits the site backend after auth (XHR/GraphQL / `page.context.request`)** → see [Authenticated backend calls](#authenticated-backend-calls) above

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
