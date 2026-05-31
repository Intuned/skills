# Webwright → Intuned Skill

The domain for an agent skill that transforms a parameterized Webwright
browser-automation script into a deployed, hosted Intuned project.

## Language

**Crafted CLI**:
The reusable, parameterized `final_script.py` produced by a Webwright `craft`
run — one domain function plus an `argparse` wrapper whose flag defaults equal
the original concrete task. The skill's input.
_Avoid_: reuse CLI, parameterized CLI, final script, reusable tool.

**Intuned API**:
A single `api/<name>.py` file exposing `async def automation(page, params, **_kwargs)`.
The unit of work in an Intuned Project; all APIs in a project deploy together.
_Avoid_: endpoint, automation script, function, handler.

**Intuned Project**:
A deployable directory (`api/`, `utils/`, `Intuned.jsonc`, `pyproject.toml`,
`.parameters/`) that groups related Intuned APIs. The skill's output.
_Avoid_: package, repo, app.

**Faithful port**:
The transformation contract — one Crafted CLI function becomes exactly one
Intuned API with identical behavior, re-fitted to Intuned's boundary (injected
`page`, typed `params`, returned result). Logic is not re-architected except
through explicitly enumerated exceptions.
_Avoid_: migration, rewrite, re-architecture.

**Params**:
The typed input to an Intuned API — a `TypedDict` plus a pydantic schema in
`utils/`, with defaults in `.parameters/api/<name>/default.json`. Mapped 1:1
from the Crafted CLI's `argparse` flags.
_Avoid_: arguments, options, inputs, config.

**Standalone run**:
A single on-demand execution of one deployed Intuned API (local
`intuned dev run api <name> '<json>'` or platform `intuned platform runs start`),
as opposed to a scheduled Job.
_Avoid_: invocation, execution, call.

**Protected site**:
A target that blocks automated traffic (fingerprint/IP/captcha). Requires
Intuned's platform-only defenses (headful + stealth mode, optionally captcha
solving and proxies) which **cannot** be exercised by a local run — so a
protected-site port is verified by a deployed `intuned platform runs start`,
not by `intuned dev run`.
_Avoid_: blocked site, hard site.
