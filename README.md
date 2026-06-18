# Intuned Skills

A collection of agent **skills** for working with [Intuned](https://intunedhq.com)
— authoring, migrating, deploying, and operating browser automations on the
Intuned platform. Install them into Claude Code, Cursor, Codex, and any other
[skills.sh](https://skills.sh)-compatible agent with one command.

## Install

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

## Skills

| Skill                                                   | What it does                                                                                                                                                                                                |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`webwright-to-intuned`](./skills/webwright-to-intuned) | Turn a [Webwright](https://github.com/microsoft/Webwright) "Crafted CLI" into a deployed, verified Intuned project. Includes 4 example crafts to port under [`examples/`](./examples/webwright-to-intuned). |

## Plugin

This repo also ships the **Intuned Agent Plugin**, it runs
the full Intuned automation agent locally in your own project: the workflow and
capability skills, the browser MCP, and the CDP hooks. It lives under
[`intuned-agent-plugin/`](./intuned-agent-plugin) and installs as a Claude Code
plugin from this repo's marketplace.

First install and sign in to the Intuned CLI (the plugin drives it):

```bash
npm install -g @intuned/cli
intuned auth login
```

Then add the marketplace and install the plugin:

```bash
claude plugin marketplace add Intuned/skills && claude plugin install intuned-agent-plugin@intuned-skills
```

Run `/reload-plugins` afterward to activate it. See
[`intuned-agent-plugin/README.md`](./intuned-agent-plugin/README.md) for what it
provides and how it works.

## Contributing

Want to add a skill? See [`CLAUDE.md`](./CLAUDE.md) for conventions.

## License

MIT — see [LICENSE](./LICENSE).
