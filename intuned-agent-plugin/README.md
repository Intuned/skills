# Intuned Agent Plugin

The **Intuned plugin** runs the Intuned automation agent locally in your own
project — build, edit, test, and debug browser automations from the command
line.

Run **`/intuned:agent`** for a guided overview of what you can do.

## Install

The plugin drives the Intuned CLI, so install and sign in first:

```bash
npm install -g @intuned/cli
intuned auth login
```

Then add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add Intuned/skills
/plugin install intuned-agent-plugin@intuned-skills
```

Run `/reload-plugins` to activate. The browser tooling also needs `uv` + Python
on your `PATH` (the MCP server launches via `uvx intuned-agent-mcp`).

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
| [`trace-debugging`](./skills/trace-debugging)               | Debug an automation failure from its Playwright trace (`.zip`).                           |

### Non-invocable skills

Meant for the agent's use — it loads these automatically as needed; you don't
call them directly.

| Skill                                                     | What it does                                      |
| --------------------------------------------------------- | ------------------------------------------------- |
| [`intuned-overview`](./skills/intuned-overview)           | Core concepts: projects, APIs, jobs, attachments. |
| [`initialize-project`](./skills/initialize-project)       | Scaffold an empty workspace into a project.       |
| [`implement-api`](./skills/implement-api)                 | Write correct, robust API code.                   |
| [`build-selectors`](./skills/build-selectors)             | Build reliable selectors via the browser tools.   |
| [`find-network-requests`](./skills/find-network-requests) | Find the backend request an API depends on.       |
| [`intuned-browser`](./skills/intuned-browser)             | Browser helper library reference.                 |
| [`browser-management`](./skills/browser-management)       | Start/stop the local browser and tabs.            |
| [`auth-sessions`](./skills/auth-sessions)                 | Login flows and authenticated access.             |
| [`handle-attachments`](./skills/handle-attachments)       | Capture downloadable files as attachments.        |
| [`manage-jobs`](./skills/manage-jobs)                     | Create and manage Jobs (`.job.json`).             |
| [`manage-env-vars`](./skills/manage-env-vars)             | Env vars and secrets for APIs.                    |
| [`project-settings`](./skills/project-settings)           | `Intuned.json` configuration reference.           |
| [`bot-detection`](./skills/bot-detection)                 | Get past bot blocks, IP limits, CAPTCHAs.         |
| [`proxy`](./skills/proxy)                                 | Route browser traffic through a proxy.            |
| [`platform-errors`](./skills/platform-errors)             | Diagnose platform error codes.                    |
| [`intuned-cli`](./skills/intuned-cli)                     | `intuned` CLI command reference.                  |

## Hooks

The plugin wires one Claude Code hook (see [`hooks/hooks.json`](./hooks/hooks.json)):

- **`inject-cdp.sh`** runs **before every browser tool call**
  (`mcp__plugin_intuned_browser__*`). It looks up the running local browser via
  the Intuned CLI and injects the live CDP address and tab→target map (plus the
  auth-params directory, when present) into the tool input, so the browser tools
  attach to the right browser and tab. If the browser isn't running, it blocks the
  call with a clear "start the browser" message instead of letting it fail.
