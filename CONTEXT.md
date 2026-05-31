# Intuned Skills

Shared vocabulary for the Intuned skills collection. Each skill may add a
skill-local `CONTEXT.md` (e.g. [webwright-to-intuned](./skills/webwright-to-intuned/CONTEXT.md)).

## Language

**Skill**:
A self-contained agent capability — a `skills/<name>/` folder with a `SKILL.md` —
installable via the [skills.sh](https://skills.sh) CLI.
_Avoid_: plugin, command, tool.

**Intuned Project**:
A deployable directory (`api/`, `Intuned.jsonc`, `pyproject.toml`, `.parameters/`)
that groups Intuned APIs; the unit skills here produce or operate on.
_Avoid_: package, app, repo.

**Intuned API**:
A single `api/<name>.py` exposing `async def automation(page, params, **_kwargs)`;
the deployable unit of work inside a project.
_Avoid_: endpoint, automation script, handler.
