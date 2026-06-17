# Intuned Agent Plugin

A Claude Code plugin that runs the **Intuned automation agent locally**, right in
your own project. You get the full set of Intuned authoring skills and browser
tooling, so you can build, edit, test, and debug browser automations from the
command line.

Plugin name: **`intuned`** → skills invoke as `/intuned:create-project`, etc.;
browser tools are `mcp__plugin_intuned_browser__*`.

## Prerequisites

- **`intunedctl`** on `PATH`, signed in. Install it with `npm install -g
@intuned/cli`, then run `intunedctl auth login`. All AI browser tools
  authenticate through the gateway resolved from this login.
- **`uv` + Python** for the browser MCP server. `.mcp.json` launches it with
  `uvx intuned-agent-mcp`, so `uv` just needs to be on `PATH`; it fetches and
  caches the published `intuned-agent-mcp` package on first run.

## Run it

```bash
# install + sign in
npm install -g @intuned/cli
intunedctl auth login

cd <your-project>

# fetch the plugin into ./intuned-plugin
intunedctl install plugin

# launch Claude Code with it
claude --plugin-dir ./intuned-plugin
```

`intunedctl install plugin` clones this plugin into the current directory (use
`-o <path>` to install elsewhere) and prints the exact `--plugin-dir` to use.

On session start the plugin runs `intunedctl dev agent-hooks setup`, which writes
`.intuned/hooks.json` and `.intuned/agent-hooks/` into the project so the CLI
hooks (artifact capture, result compaction, browser network tracking, etc.) are
active automatically.

## CLI hooks

`intunedctl dev agent-hooks setup` materializes the Intuned agent CLI hooks into
your project's `.intuned/` directory, and the plugin's SessionStart hook calls it
for you. Hooks are merged by name, so any hooks you add yourself are preserved.

## Stealth, CAPTCHA, and proxy

Stealth mode and the CAPTCHA solver only take effect once your project is
deployed. They don't engage during local dev, so there's nothing to exercise
locally.
