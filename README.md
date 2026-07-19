# Intuned

[Intuned](https://intunedhq.com) browser automation for your coding agent.

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
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`webwright-to-intuned`](./skills/webwright-to-intuned) | Turn a [Webwright](https://github.com/microsoft/Webwright) "Crafted CLI" into a deployed, verified Intuned project. Includes 4 example crafts to port under [`examples/`](./examples/webwright-to-intuned). |

More skills coming.

---

## Looking for the Intuned Agent Plugin?

The Intuned Agent Plugin (run the Intuned agent locally in Claude Code or
Codex) is in **private preview** and is no longer distributed from this repo.
If you'd like access, [contact our
team](https://intunedhq.com/docs/main/06-resources/help-and-support).

---

## Contributing

Want to add a skill? See [`CLAUDE.md`](./CLAUDE.md) for conventions.

## License

MIT — see [LICENSE](./LICENSE).
