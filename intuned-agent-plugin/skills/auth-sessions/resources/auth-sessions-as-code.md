# Auth Sessions as Code

Auth session resource files (`.auth-session.json`) let you define default credential sets for a project as checked-in files, similar to job files.

## File Location

```
intuned-resources/auth-sessions/<name>.auth-session.json
```

One file per credential set. For example, if `.parameters/auth-sessions/create/` contains `default.json`, the corresponding resource file is `intuned-resources/auth-sessions/default.auth-session.json`.

## File Format

```json
{
  "parameters": {
    // <parameters copied from .parameters/auth-sessions/create/<name>.json>
  }
}
```

## When to Create

- When creating a project that has auth sessions enabled.
- When the user explicitly asks to create or configure a default auth session.

## How to Create (auth-sessions-as-code approach)

Because `.parameters/auth-sessions/create/*.json` files contain sensitive credentials, **do NOT read or echo them directly**. Instead, run the `auth-sessions` skill's bundled `scripts/create-auth-sessions.sh` — the path is relative to that skill's directory, and run it with the project root as the working directory:

```bash
scripts/create-auth-sessions.sh
```

It generates one `.auth-session.json` per credential set found in `.parameters/auth-sessions/create/`, writing credential values directly to disk without exposing them in shell output.

## When Resource Files Take Effect

Like Code-origin job files (`intuned-resources/jobs/*.job.json`), auth session resource files are applied once the project is deployed.
