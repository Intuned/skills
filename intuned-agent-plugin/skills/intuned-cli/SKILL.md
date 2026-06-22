---
name: intuned-cli
user-invocable: false
description: "Reference for the intuned CLI — what each command does and when to use it. Load when you need the right command for a browser, dev, or platform operation. Also includes CLI-Hooks guide and how-to install."
---

# Intuned CLI

`intuned` cli has two command families: **`dev`** for local development and browser automation, and **`platform`** for managing deployed platform resources. Each command below points to a resource with full flags and usage — read it for the command you need.

## `intuned dev` — local development

```bash
intuned dev --help
```

- **`intuned dev browser`**: Manage persistent browser instances. Includes information about how to start, stop, and check the status of browsers, as well as how to manage tabs.
  - Read more at `resources/dev_browser.md`
- **`intuned dev attempt`**: Execute single Intuned attempts (no retry logic) — `attempt api`, `attempt authsession check`, `attempt authsession create`. Use this for fast iterative development.
  - Read more at `resources/dev_attempt.md`
- **`intuned dev run`**: Execute full Runs locally with retry logic — `run api`, `run authsession create|validate|update`. Use this when you need behavior closer to production.
  - Read more at `resources/dev_run.md`
- **`intuned dev stealth`** / **`intuned dev captcha-solve`**: Write stealth-mode / CAPTCHA-solver config into `Intuned.json`. Configure them now and they take effect once the project runs on the platform — they don't engage during local dev, so there's nothing to validate locally. See the `bot-detection` skill for the full picture.
  - Read more at `resources/dev_stealth.md` and `resources/dev_captcha_solve.md`
- **`intuned dev proxy`**: Set or clear a normal user-supplied dev (and optionally deployed) proxy. Restarts the browser by default. This is the one anti-bot lever that works locally.
  - Read more at `resources/dev_proxy.md`
- **`intuned dev list-templates`**: List available project templates. Filter to the starter templates with `--tag starter` (use this when initializing a new project); `--language <lang>` filters by language and `--json` gives JSON output.
- **`intuned dev init`**: Initialize a new Intuned project from a template or GitHub URL. Use `--template <id>`, `--language <lang>`, and `--non-interactive` for non-interactive usage.
  - The command errors if any file it is about to write already exists — unrelated files in the directory are ignored
  - `--overwrite`: force overwrite files that already exist (use when re-initializing over an existing project)
  - `--stealth`: enable stealth mode in `Intuned.json` from the start
  - `--captcha-solve`: enable the captcha solver in `Intuned.json` with all providers pre-configured

## `intuned platform` — deployed platform resources

```bash
intuned platform --help
```

Interacts directly with the Intuned platform for projects already deployed there: Jobs, Runs, Project information, and Test Job Runs. For deeper context, load the relevant skill — `manage-jobs` (jobs), `platform-errors` (run/attempt errors), `project-settings` (`Intuned.json` config), or `intuned-overview` (how it all fits together).

## Provisioning and Deploying (available)

As a customer, you **can** provision and deploy your own projects:

- **`intuned dev provision`** — register a project on the Intuned platform (creates the platform-side project; does **not** deploy or run anything). Needed for project-scoped env vars and as the prerequisite for `dev deploy`. The `create-intuned-project` flow provisions the project early, right after init.
- **`intuned dev deploy`** — deploy the current project to the Intuned platform. Use this to push your code so it runs on the platform, and so platform-only features (stealth mode, CAPTCHA solver) take effect and can be validated with deployed runs / `intuned dev test-job`.

## Analyzing deployed projects

Use the platform commands below to analyze runs, download logs, and inspect traces for already-deployed projects:

- **`intuned platform attempts`**: Get information about a single Job run attempt. Useful for getting information on a failed run.
  - Read more at `resources/platform_attempt.md`
- **`intuned dev test-job`**: Run and manage test executions on the platform.
  - Read more at `resources/platform_test.md`
- **`intuned platform runs`**: Get information about a specific run and its attempts.
  - Read more at `resources/platform_runs.md`
- **`intuned platform jobs`**: Manage automation jobs — create, list, inspect, trigger, update, pause, resume, and delete jobs.
  - Before creating or editing any job, load the `manage-jobs` skill for job origin rules, name-uniqueness checks, and the correct workflow.
  - Read more at `resources/platform_jobs.md`
- **`intuned platform jobruns`**: List, inspect, and terminate individual job runs.
  - Read more at `resources/platform_jobruns.md`
- **`intuned platform project`**: Get information about the current project on the platform.
  - Read more at `resources/platform_project.md`
- **`intuned platform issues`**: List and inspect issues detected on the platform for a project.
  - Read more at `resources/platform_issues.md`
- **`intuned platform authsessions`**: Create, inspect, validate, update, and delete platform auth sessions.
  - Read more at `resources/platform_authsessions.md`
- **`intuned platform env-vars`**: Manage **project-scoped** environment variables — list, get, create, update, delete.
  - Read more at `resources/platform_env_vars.md`. For _which_ store to use and the AUTHORING/PUBLISHED rule, load the `manage-env-vars` skill.
- **`intuned platform workspace env-vars`**: Manage **workspace-scoped** environment variables shared across all projects in the workspace.
  - Read more at `resources/platform_workspace_env_vars.md`. See the `manage-env-vars` skill for choosing between local/project/workspace stores.

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.

## CLI Hooks

Intuned CLI hooks are event handlers for the `intuned` commands, they fire around
every command it runs (`onCommandStart` / `onCommandComplete`), receiving the
command and its result as JSON on stdin. They are **not** Claude Code hooks.

You can install them by running this command:

```bash
intuned dev agent-hooks setup
```

This writes the hook scripts into `.intuned/agent-hooks/` and registers them in
`.intuned/hooks.json`. It installs 5 hooks:

- **`validate-output-path.ts`** (`onCommandStart`): For `platform attempts trace` / `log`, injects a default `-o` output path under `.intuned-agent/platform-attempts/<runId>/` when the user didn't pass one — so results always land in a known place.
- **`artifacts-command-start-mutation.ts`** (`onCommandStart`): For API and auth-session attempt commands: creates the run directory under the artifacts root, redirects the command's output there, and obfuscates sensitive parameter values (e.g. auth-session credentials).
- **`artifacts-command-events-capture.ts`** (command lifecycle): Records command start/complete events and writes result and metadata artifacts into the per-run folder under `.intuned-agent/`.
- **`network-tracking-hint.sh`** (`onCommandComplete`): On browser start or tab create, prints where the tab's network traces are recorded (`.intuned-agent/tab_<id>/network/`).
- **`cleanup-tab-data.sh`** (`onCommandComplete`): On browser stop, tab close, or stealth/captcha toggle, removes the matching `.intuned-agent/tab_*` folders.
