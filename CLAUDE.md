# Contributing skills to intuned-skills

This repo is a [skills.sh](https://skills.sh)-installable collection. Each skill
is a folder under `skills/<category>/<name>/` with a `SKILL.md` at its root.

## Layout rules
- One skill = one folder. The folder name is the skill's invocable name and must
  match the `name:` in its `SKILL.md` frontmatter (lowercase, hyphenated).
- `SKILL.md` frontmatter needs `name` and a trigger-rich, third-person
  `description` (what it does + when to use it, with literal user phrases). This
  is the only thing always loaded, so keep it tight.
- Keep the `SKILL.md` body lean; push detail into `reference/`, decisions into
  `docs/adr/`, vocabulary into a skill-local `CONTEXT.md`. Slash commands go in
  `commands/`.
- Register every skill folder in `.claude-plugin/plugin.json`'s `skills` array —
  the `skills` CLI reads that file. An unregistered folder won't install.

## Categories
Group by task type, not by surface (everything here targets Intuned). Current:
`migration` (onboard external automations onto Intuned). Add categories like
`authoring`, `debugging`, `ops` as skills arrive.

## Checklist before adding
- [ ] `skills/<category>/<name>/SKILL.md` exists with valid frontmatter
- [ ] path added to `.claude-plugin/plugin.json`
- [ ] row added to the README Skills table
- [ ] `npx skills@latest add <thisrepo> --skill <name>` installs cleanly
- [ ] description triggers on the intended prompts and nothing unrelated
