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
- Keep the `SKILL.md` body lean; push detail into `.md` files in a **`resources/`
  subfolder** beside it, and have `SKILL.md` point at them (`resources/<doc>.md`).
  Executable helpers go in a `scripts/` subfolder. Per-skill demo assets live at
  the repo level under `examples/<name>/`, not inside the skill.
- The `skills` CLI discovers skills by **scanning for `SKILL.md`** under `skills/`
  — nothing to register; a new skill folder installs as soon as it exists.

## Checklist before adding
- [ ] `skills/<name>/SKILL.md` exists with valid frontmatter
- [ ] supporting docs live in the skill's `resources/` subfolder
- [ ] row added to the README Skills table
- [ ] `npx skills@latest add Intuned/skills --skill <name>` installs cleanly
- [ ] description triggers on the intended prompts and nothing unrelated
