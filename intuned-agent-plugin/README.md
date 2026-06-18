# Intuned Agent Plugin

A Claude Code plugin that brings the **Intuned automation agent** into your
workflow — build, edit, test, and debug browser automations locally, right in
your own project, from the command line.

Plugin name: **`intuned`** → skills invoke as `/intuned:create-intuned-project`,
etc.; browser tools are `mcp__plugin_intuned_browser__*`.

## Features

- **Project authoring skills** — scaffold, implement, and ship Intuned projects:
  `initialize-project`, `create-intuned-project`, `implement-api`,
  `edit-intuned-project`, `test-intuned-project`, `project-settings`.
- **Browser automation** — navigation, waiting, content extraction, pagination,
  and file handling via the `intuned-browser` skill and the bundled browser MCP
  server.
- **Selector & network tooling** — `build-selectors`, `find-network-requests`,
  and `trace-debugging` for authoring reliable automations and debugging runs.
- **Platform operations** — `manage-jobs`, `manage-env-vars`,
  `handle-attachments`, `auth-sessions`, and `proxy` for the full Intuned
  platform surface.
- **Resilience helpers** — `bot-detection`, `platform-errors`, and
  `investigate-and-fix` for diagnosing and hardening automations.
- **Live docs** — the `intuned-docs` MCP server exposes Intuned documentation
  directly to the agent.
- **Automatic CLI hooks** — a SessionStart hook wires up artifact capture,
  result compaction, and browser network tracking with no manual setup.

## Installation

```bash
claude plugin marketplace add Intuned/skills && claude plugin install intuned@intuned-skills
```

The first command registers the Intuned marketplace; the second installs the
plugin. Run `/reload-plugins` afterward to activate it in an existing session.

## Usage

### Skills

Skills are namespaced by the plugin name. Start a new project and implement an
API:

```text
/intuned:create-intuned-project
/intuned:implement-api
/intuned:test-intuned-project
```

Editing or debugging an existing project:

```text
/intuned:edit-intuned-project
/intuned:investigate-and-fix
/intuned:trace-debugging
```

The agent also invokes these skills automatically when a prompt matches — e.g.
asking it to "fix the selector on the login page" pulls in `build-selectors`.

### Browser MCP tools

The bundled `browser` MCP server provides browser-automation tools under the
`mcp__plugin_intuned_browser__*` namespace (navigation, extraction, pagination,
file handling). The agent calls these while authoring and running automations.

### Hooks

- **SessionStart** runs `intuned dev agent-hooks setup`, materializing the CLI
  hooks into your project's `.intuned/` directory (artifact capture, result
  compaction, network tracking). Hooks are merged by name, so any hooks you add
  yourself are preserved.
- **PreToolUse** injects CDP connection details before each browser tool call.

## Configuration

- **AI gateway** — all AI browser tools authenticate through the gateway
  resolved from your `intuned auth login` session (`INTUNED_USE_CLI_AI_GATEWAY`).
- **Docs MCP** — the `intuned-docs` server points at
  `https://intunedhq.com/docs/mcp`.
- **Stealth, CAPTCHA, and proxy** — stealth mode and the CAPTCHA solver only
  engage once your project is **deployed**; they do not run during local dev, so
  there is nothing to exercise locally. Proxy configuration is managed through
  the `proxy` skill and project settings.

## Requirements

- **`intuned` CLI** on `PATH`, signed in:

  ```bash
  npm install -g @intuned/cli
  intuned auth login
  ```

- **`uv` + Python** for the browser MCP server. `.mcp.json` launches it with
  `uvx intuned-agent-mcp`, so `uv` just needs to be on `PATH`; it fetches and
  caches the published `intuned-agent-mcp` package on first run.
