# Intuned Agent Plugin

The **Intuned plugin** runs the Intuned automation agent locally in your own
project — build, edit, test, and debug browser automations from the command
line.

Run **`/intuned:agent`** for a guided overview of what you can do.

## Requirements

- **Intuned CLI**, installed and signed in — the plugin drives it:

  ```bash
  npm install -g @intuned/cli
  intuned auth login
  ```

- **`uv`** on your `PATH` — uv provides the Python the browser tooling needs and
  launches the MCP server via `uvx intuned-agent-mcp`. Install it with the
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Install

Open Claude Code and run these commands to add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add Intuned/skills
/plugin install intuned-agent-plugin@intuned-skills
/reload-plugins
```

Then run this command to get started with the agent, it will show an overview of what is the agent capable of:

```text
/intuned:agent
```

Skills invoke under the `intuned` namespace (e.g. `/intuned:create-intuned-project`);
browser tools are `mcp__plugin_intuned_browser__*`.

## Available skills

User-invocable — call them directly, or just describe what you want and the agent
picks the right one:

| Skill                                                       | What it does                                                                              |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`agent`](./skills/agent)                                   | Overview of the plugin — what Intuned is, what you can ask for, and recommended patterns. |
| [`create-intuned-project`](./skills/create-intuned-project) | Build a new automation for a site — scraping, crawling, RPA, or actions.                  |
| [`edit-intuned-project`](./skills/edit-intuned-project)     | Add, change, or fix APIs in an existing project.                                          |
| [`test-intuned-project`](./skills/test-intuned-project)     | Run an API locally or as an end-to-end platform test job.                                 |
| [`investigate-and-fix`](./skills/investigate-and-fix)       | Diagnose and fix a failing run or wrong data.                                             |
| [`fix-open-issues`](./skills/fix-open-issues)               | Sweep, triage, and fix all open issues on the project.                                    |
| [`trace-debugging`](./skills/trace-debugging)               | Debug an automation failure from its Playwright trace (`.zip`).                           |

### Non-invocable skills

Meant for the agent's use — it loads these automatically as needed; you don't
call them directly.

| Skill                                                     | What it does                                       |
| --------------------------------------------------------- | -------------------------------------------------- |
| [`intuned-overview`](./skills/intuned-overview)           | Core concepts: projects, APIs, jobs, attachments.  |
| [`initialize-project`](./skills/initialize-project)       | Scaffold an empty workspace into a project.        |
| [`implement-api`](./skills/implement-api)                 | Write correct, robust API code.                    |
| [`build-selectors`](./skills/build-selectors)             | Build reliable selectors via the browser tools.    |
| [`find-network-requests`](./skills/find-network-requests) | Find the backend request an API depends on.        |
| [`intuned-browser`](./skills/intuned-browser)             | Browser helper library reference.                  |
| [`browser-management`](./skills/browser-management)       | Start/stop the local browser and tabs.             |
| [`auth-sessions`](./skills/auth-sessions)                 | Login flows and authenticated access.              |
| [`handle-attachments`](./skills/handle-attachments)       | Capture downloadable files as attachments.         |
| [`manage-jobs`](./skills/manage-jobs)                     | Create and manage Jobs (`.job.json`).              |
| [`manage-env-vars`](./skills/manage-env-vars)             | Env vars and secrets for APIs.                     |
| [`project-settings`](./skills/project-settings)           | `Intuned.json` configuration reference.            |
| [`bot-detection`](./skills/bot-detection)                 | Get past bot blocks, IP limits, CAPTCHAs.          |
| [`proxy`](./skills/proxy)                                 | Route browser traffic through a proxy.             |
| [`platform-errors`](./skills/platform-errors)             | Diagnose platform error codes.                     |
| [`self-healing`](./skills/self-healing)                   | How the platform raises, groups & resolves Issues. |
| [`intuned-cli`](./skills/intuned-cli)                     | `intuned` CLI command reference.                   |
