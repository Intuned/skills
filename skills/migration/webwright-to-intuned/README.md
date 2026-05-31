# webwright-to-intuned

A Claude Code / Codex **skill** that turns a [Webwright](https://github.com/microsoft/Webwright)
**Crafted CLI** — the parameterized `final_script.py` produced by a `webwright craft`
run — into a deployed, hosted **[Intuned](https://intunedhq.com)** project, and
verifies it end to end.

A parameterized Webwright function maps almost 1:1 onto an Intuned API. This skill
makes that mapping a deterministic, testable transform instead of a hand re-write:

```
Webwright craft (final_script.py + argparse)
        │   /intuned-port <craft-dir>
        ▼
Intuned project  ──►  intuned dev run  ──►  intuned dev deploy  ──►  intuned platform runs start
   api/<name>.py        (local gate)          (deploy)               (verified standalone run)
```

## What it does

- **Faithful 1:1 port** (default): one craft function → one `async def automation(page, params)`
  API. It strips the craft's browser bootstrap (the platform injects `page`), maps
  `argparse` flags to typed `params` (dropping harness-only params), swaps
  `page.goto` → `go_to_url`, drops local file/screenshot artifacts, and makes the
  default params reproduce the original task.
- **Auth as AuthSessions**: a login craft is decomposed into `auth-sessions/create.py`
  + `check.py` so the automation runs already-authenticated.
- **Protected sites**: enables stealth/headful in `Intuned.jsonc` and treats the
  **deployed** run as the real gate (stealth/captcha don't run locally).
- **Self-verifies**: scaffolds, runs locally, deploys, and triggers a standalone
  platform run — and folds every failure into a growing gotchas list.

## Repository layout

| Path | What |
|---|---|
| [`SKILL.md`](./SKILL.md) | The skill entry point (auto-activates). |
| [`commands/intuned-port.md`](./commands/intuned-port.md) | The `/intuned-port <craft-dir>` command. |
| [`reference/transformation-rules.md`](./reference/transformation-rules.md) | The step-by-step transform + gates. |
| [`reference/intuned-contract.md`](./reference/intuned-contract.md) | The exact Intuned target (API signature, SDK, CLI, manifest). |
| [`reference/gotchas.md`](./reference/gotchas.md) | Hardening layer — 14 traps a coding agent falls into. |
| [`CONTEXT.md`](./CONTEXT.md) | Canonical vocabulary. |
| [`docs/adr/`](./docs/adr/) | The three load-bearing decisions. |
| [`docs/TEST-RESULTS.md`](./docs/TEST-RESULTS.md) | End-to-end verification record. |
| [`examples/`](./examples/) | **Four ready-to-convert demonstrations** — 2 sandbox + 2 real-site (see below). |

## Examples — convert these to see the skill work

Four demonstrations: **two on Intuned's public sandbox** (always reproducible) and
**two on real third-party sites**. Each ships the **craft input** *and* a
**reference converted Intuned project** so you can diff before/after.

| Example | Group | Demonstrates | Convert with |
|---|---|---|---|
| [`examples/sandbox/pdf-crawl`](./examples/sandbox/pdf-crawl) | sandbox | **Faithful port** — crawl → flat list (no fan-out). | `/intuned-port examples/sandbox/pdf-crawl/craft` |
| [`examples/sandbox/login`](./examples/sandbox/login) | sandbox | **AuthSessions exception** — login → `create.py`/`check.py`. | `/intuned-port examples/sandbox/login/craft` |
| [`examples/real/techcrunch-startup-news`](./examples/real/techcrunch-startup-news) | real site | Faithful scrape + params; drops a harness param. | `/intuned-port examples/real/techcrunch-startup-news/craft` |
| [`examples/real/books-discover`](./examples/real/books-discover) | real site | Faithful crawl across full pagination. | `/intuned-port examples/real/books-discover/craft` |

See [`examples/README.md`](./examples/README.md) for the full before/after walkthrough.

## Prerequisites

- The [Intuned CLI](https://intunedhq.com/docs/main/05-references/cli/overview)
  installed and authenticated (`intuned auth whoami`).
- A Webwright craft output directory to port (or use the bundled examples).

## Install

Drop the skill where your agent loads skills, e.g. for Claude Code:

```bash
ln -s "$(pwd)" ~/.claude/skills/webwright-to-intuned
# then, in a new session:  /intuned-port examples/sandbox/pdf-crawl/craft
```

## License

MIT — see [LICENSE](./LICENSE).
