# Contributing skills to intuned-skills

This repo is a [skills.sh](https://skills.sh)-installable collection. Each skill
is a folder under `skills/<name>/` with a `SKILL.md` at its root (flat — no
category folders).

## Layout rules
- One skill = one folder. The folder name is the skill's invocable name and must
  match the `name:` in its `SKILL.md` frontmatter (lowercase, hyphenated).
- `SKILL.md` frontmatter needs `name` and a trigger-rich, third-person
  `description` (what it does + when to use it, with literal user phrases). This
  is the only thing always loaded, so keep it tight.
- Keep the `SKILL.md` body lean; push detail into **flat `.md` files beside it**
  (the skills.sh convention — no `reference/`, `docs/`, or `commands/`
  subfolders). Executable helpers go in a `scripts/` subfolder. Per-skill demo
  assets live at the repo level under `examples/<name>/`, not inside the skill.
- Register every skill folder in `.claude-plugin/plugin.json`'s `skills` array —
  the `skills` CLI reads that file. An unregistered folder won't install.

## Checklist before adding
- [ ] `skills/<name>/SKILL.md` exists with valid frontmatter
- [ ] supporting docs are flat `.md` beside `SKILL.md` (no `commands/`/`reference/`)
- [ ] path added to `.claude-plugin/plugin.json`
- [ ] row added to the README Skills table
- [ ] `npx skills@latest add Intuned/skills --skill <name>` installs cleanly
- [ ] description triggers on the intended prompts and nothing unrelated
