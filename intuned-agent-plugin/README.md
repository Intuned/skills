# Intuned Agent Plugin

A Claude Code plugin that runs the **Intuned automation agent** locally in your
own project — build, edit, test, and debug browser automations from the command
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

The agent loads skills automatically from plain-English requests — you never have
to name them. The main entry points:

### `agent`

Start here. What Intuned is, what you can ask for, and recommended patterns. Use
when you run `/intuned:agent`, ask "what can you do", or "how do I get started".

### `create-intuned-project`

Build a new automation for a site — scraping, crawling, RPA, or action
workflows. Use when there's no project yet for what you want done.

### `edit-intuned-project`

Change, add, or fix something in an existing project — a new API, adjusted
fields, a new page to handle, a break to repair.

### `test-intuned-project`

Run your automation locally or as an end-to-end platform test job.

### `investigate-and-fix` / `trace-debugging`

Diagnose and fix failing runs. `trace-debugging` handles Playwright trace files
(`.zip`).

Plus capability skills the agent pulls in as needed: browser control, selector
building, network requests, auth sessions, jobs, env vars, attachments, bot
detection, proxies, and platform concepts.
