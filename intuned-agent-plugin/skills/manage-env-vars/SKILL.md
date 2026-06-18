---
name: manage-env-vars
description: "Give an Intuned project's APIs the environment variables and secrets they need (API keys, tokens, endpoints, config) — deciding between a local `.env`, project-scoped, or workspace-scoped store, and getting the AUTHORING/PUBLISHED environments right so the value is actually available where it runs. Load when an API needs a secret or configurable value, or when you're collecting config that isn't an auth-session login."
---

# Environment Variables & Secrets

The capability is supplying values an API shouldn't have hard-coded — API keys, auth tokens, base URLs, account IDs, feature flags — and storing each one where it will actually be readable when the code runs. This is **not** for auth-session logins (those live in `.parameters/auth-sessions/` — see the `auth-sessions` skill); it's for everything else an API reads from the environment.

## Core rules

- **Never hard-code a secret** into an API file or commit it. Read it from the environment instead.
- **Never handle the value yourself.** Don't ask the user to paste a secret into the chat, and don't run a command with the secret as an argument. You decide the **key name** and which store to use, then **hand the user the command to run** (for a platform var) or **ask them to add the line to `.env`** — the value goes straight to storage and never passes through you. Tell the user which keys are needed (and which are required) all at once.
- **Read values from the environment in code:**
  - Python: `os.environ["MY_KEY"]` (or `os.getenv("MY_KEY")` for an optional default).
  - TypeScript: `process.env.MY_KEY`.

## Where to store — three places

| Store                 | How (the user does this — `<value>` is their placeholder to fill)                                                            | Scope                          | Best for                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------- |
| **Local `.env`**      | ask the user to add `KEY=<value>` to `.env` at the project root (git-ignored)                                                | local dev only                 | Local-only builds, quick iteration, values you don't want on the platform |
| **Project env var**   | give the user this to run: `intuned platform env-vars create --key KEY --value <value> --envs AUTHORING,PUBLISHED`           | this project                   | Per-project secrets that also work in deployed runs                       |
| **Workspace env var** | give the user this to run: `intuned platform workspace env-vars create --key KEY --value <value> --envs AUTHORING,PUBLISHED` | every project in the workspace | Shared keys reused across projects (common API keys, service creds)       |

You provide the exact command (or `.env` line) with the real key name and a `<value>` placeholder; **the user fills the value and runs it / saves the file themselves.** Don't substitute the value or run the command yourself. The `intuned-cli` skill has the full flag reference for `platform env-vars` and `platform workspace env-vars`.

## The `--envs` rule — the part that's easy to get wrong

Each platform env var is exposed to one or both **environments**, set with `--envs`:

- **`AUTHORING`** — available during local/dev/agent work, i.e. to `intuned dev attempt` and `intuned dev run`.
- **`PUBLISHED`** — available in deployed (production) runs.

**The default is `PUBLISHED` only.** A var created with the default is **NOT visible to local `dev attempt`/`dev run`** — only after deploy. So:

- To use a platform env var **during the local build**, it must include **`AUTHORING`**.
- To use it **after deploy** too, include **`PUBLISHED`**.
- **Default to `--envs AUTHORING,PUBLISHED`** so the value works both while you build and once the project is live. Narrow it only when the user wants the value to exist in just one environment.

A local **`.env`** value is always available in local dev (no `--envs` concept) but never ships to the platform.

## Resolution & override order (local dev)

When `dev attempt`/`dev run` build the environment, values resolve in this order (later overrides earlier):

1. **Workspace** `AUTHORING` vars
2. **Project** `AUTHORING` vars (override workspace on key clash)
3. **`.env` / `process.env`** (override remote vars on key clash)

So a key in `.env` wins locally over the same key stored on the platform. Before creating a new platform var, you can check whether it already exists at workspace level (`intuned platform workspace env-vars list`) so you don't shadow it unintentionally.

## Quick recipe

1. Identify what the API needs (key names, which are required).
2. Pick the store:
   - local-only → **`.env`**;
   - shared across projects → **workspace** env var with `--envs AUTHORING,PUBLISHED`;
   - per-project → **project** env var with `--envs AUTHORING,PUBLISHED`.
3. **Hand the user the exact `.env` line or command to run, with a `<value>` placeholder** — they fill the real value. Never paste it into chat, never run it yourself with the secret.
4. Read the values in code via `os.environ` / `process.env`.
5. Confirm each value is in the right place for where it runs (AUTHORING / `.env` for local, PUBLISHED for deployed).

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
