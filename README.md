# Intuned

[Intuned](https://intunedhq.com) browser automation for your coding agent.

## Intuned Agent Plugin

The full Intuned automation agent, running locally in your own project: the
workflow and capability skills, the browser MCP, and the CDP hooks. Use it to
build, edit, test, and debug browser automations from the command line.

Requirements:

- **Intuned CLI**, installed and signed in — the plugin drives it:

  ```bash
  npm install -g @intuned/cli
  intuned auth login
  ```

- **`uv`** on your `PATH` — uv provides the Python the browser tooling needs and
  launches the MCP server via `uvx intuned-agent-mcp`. Install it with the
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Claude Code

Open Claude Code and run these commands to add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add Intuned/skills
/plugin install intuned-agent-plugin@intuned-skills
/reload-plugins
```

Run `/intuned:agent` for an overview.

### Codex

Add this repo as a plugin marketplace, then install:

```bash
codex plugin marketplace add Intuned/skills
codex plugin add intuned@intuned-skills
```

(Or browse and install interactively via `/plugins` inside Codex.) Then start a
new session and invoke `$intuned:agent` — or just describe what you want
automated.

**Recommended sandbox config** — the plugin drives the `intuned` CLI, which
needs network access and a few home-directory paths that Codex's default
`workspace-write` sandbox blocks. Add this to `~/.codex/config.toml` to avoid
an approval prompt on every command:

```toml
[sandbox_workspace_write]
network_access = true
writable_roots = ["~/.intuned", "~/.npm", "~/.cache"]
```

One exception remains: `intuned dev browser start` cannot run inside the macOS
sandbox (Chromium's process model requires mach-port registration the sandbox
denies) — approve the one-time escalation Codex requests for it; everything
after that runs sandboxed.

Alternatively, run Codex with the sandbox disabled
(`codex --sandbox danger-full-access`) — no config needed, but the config
above is the safer option.

See [`intuned-agent-plugin/`](./intuned-agent-plugin) for what the plugin
provides and how it works.

---

## Intuned Skills

A collection of agent **skills** for working with Intuned — authoring,
migrating, deploying, and operating browser automations on the Intuned platform.
Install them into Claude Code, Cursor, Codex, and any other
[skills.sh](https://skills.sh)-compatible agent with one command.

All skills at once, via the [`skills` CLI](https://skills.sh):

```bash
npx skills@latest add Intuned/skills
```

A single skill:

```bash
npx skills@latest add Intuned/skills --skill webwright-to-intuned
```

Update later with `npx skills@latest update`. No `skills` CLI? Run
`scripts/install-local.sh` to symlink the skills straight into `~/.claude/skills/`.

### Available skills

| Skill                                                   | What it does                                                                                                                                                                                                |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`webwright-to-intuned`](./skills/webwright-to-intuned) | Turn a [Webwright](https://github.com/microsoft/Webwright) "Crafted CLI" into a deployed, verified Intuned project. Includes 4 example crafts to port under [`examples/`](./examples/webwright-to-intuned). |

More skills coming.

---

## Contributing

Want to add a skill? See [`CLAUDE.md`](./CLAUDE.md) for conventions.

## License

MIT — see [LICENSE](./LICENSE).
