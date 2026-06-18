# Intuned Skills

Agent skills and the **Intuned Agent Plugin** for building, editing, testing, and
debugging browser automations on [Intuned](https://intunedhq.com) — packaged for
the open Agent Skills ecosystem and installable with the [`skills`](https://skills.sh)
CLI or as a Claude Code plugin.

## Install the plugin (Claude Code)

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

Run `/reload-plugins` to activate, then `/intuned:intuned` for an overview. See
[`intuned-agent-plugin/README.md`](./intuned-agent-plugin) for details.

## Install skills (Agent Skills CLI)

All skills at once:

```bash
npx skills@latest add Intuned/skills
```

A single skill:

```bash
npx skills@latest add Intuned/skills --skill webwright-to-intuned
```

Update later with `npx skills@latest update`.

## What's included

### Intuned Agent Plugin

Runs the full Intuned automation agent locally in your own project — the workflow
and capability skills, the browser MCP, and the CDP hooks. Lives under
[`intuned-agent-plugin/`](./intuned-agent-plugin).

### Skills

| Skill                                                   | What it does                                                                                                                                                                                                |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`webwright-to-intuned`](./skills/webwright-to-intuned) | Turn a [Webwright](https://github.com/microsoft/Webwright) "Crafted CLI" into a deployed, verified Intuned project. Includes 4 example crafts to port under [`examples/`](./examples/webwright-to-intuned). |

## Contributing

Want to add a skill? See [`CLAUDE.md`](./CLAUDE.md) for conventions.

## License

MIT — see [LICENSE](./LICENSE).
