# Intuned Skills

A collection of agent **skills** for working with [Intuned](https://intunedhq.com)
— authoring, migrating, deploying, and operating browser automations on the
Intuned platform. Install them into Claude Code, Cursor, Codex, and any other
[skills.sh](https://skills.sh)-compatible agent with one command.

## Install

All skills at once, via the [`skills` CLI](https://skills.sh):

```bash
npx skills@latest add intunedhq/skills
```

A single skill:

```bash
npx skills@latest add intunedhq/skills --skill webwright-to-intuned
```

This symlinks each skill into every selected agent's skills directory (e.g.
`~/.claude/skills/<name>`) and records them in `~/.agents/.skill-lock.json`.
Update later with `npx skills@latest update`.

> **No `skills` CLI?** Run `scripts/install-local.sh` to symlink the skills in
> this repo straight into `~/.claude/skills/`.

## Skills

| Skill | What it does |
|---|---|
| [`webwright-to-intuned`](./skills/webwright-to-intuned) | Turn a [Webwright](https://github.com/microsoft/Webwright) "Crafted CLI" into a deployed, verified Intuned project. Includes 4 convert-and-compare examples under [`examples/`](./examples/webwright-to-intuned). |

_More Intuned skills land here over time (authoring from a spec, debugging failed
runs, AuthSession setup, deploy/ops helpers, …)._

## Repository layout

```
intuned-skills/
├── .claude-plugin/
│   └── plugin.json          # lists every skill folder — the file the skills CLI reads
├── skills/
│   └── <name>/              # one folder per skill (flat, no category folders)
│       ├── SKILL.md         # required: frontmatter (name + description) + instructions
│       ├── *.md             # optional flat reference docs beside SKILL.md
│       └── scripts/         # optional executable helpers
├── examples/<name>/         # optional, per-skill demo assets (kept out of the skill folder)
├── scripts/install-local.sh # symlink installer for non-CLI users
├── CONTEXT.md               # shared vocabulary across skills
├── CLAUDE.md                # how to add a skill (contributor guide)
├── LICENSE
└── README.md
```

## Adding a skill

1. Create `skills/<your-skill>/SKILL.md` with YAML frontmatter (`name`,
   trigger-rich `description`) and lean instructions; offload detail to flat
   `.md` files beside it.
2. Add its path to the `skills` array in `.claude-plugin/plugin.json`.
3. Add a row to the **Skills** table above.

See [`CLAUDE.md`](./CLAUDE.md) for conventions.

## License

MIT — see [LICENSE](./LICENSE).
