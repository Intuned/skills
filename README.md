# Intuned

[Intuned](https://intunedhq.com) browser automation for your coding agent.

## Intuned Agent Plugin

The full Intuned automation agent, running locally in your own project: the
workflow and capability skills, the browser MCP, and the CDP hooks. Use it to
build, edit, test, and debug browser automations from the command line.

It drives the Intuned CLI, so install and sign in first:

```bash
npm install -g @intuned/cli
intuned auth login
```

Then add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add Intuned/skills
/plugin install intuned-agent-plugin@intuned-skills
```

Run `/reload-plugins` to activate, then `/intuned:agent` for an overview. See
[`intuned-agent-plugin/`](./intuned-agent-plugin) for what it provides and how it
works.

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
