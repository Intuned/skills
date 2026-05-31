---
name: webwright-to-intuned
description: >-
  Transform a Webwright "Crafted CLI" (the parameterized final_script.py produced
  by a `webwright craft` run) into a deployed, hosted Intuned project. Use when
  the user wants to port, convert, host, or deploy a Webwright craft/reusable CLI
  to Intuned, or says "turn this craft into an Intuned project", "host this on
  Intuned", "/intuned-port". Faithfully maps one parameterized craft function to
  one Intuned `automation` API, scaffolds the project, runs it locally, deploys
  it, and verifies a standalone platform run.
---

# Webwright → Intuned

Port a Webwright **Crafted CLI** into a **deployed Intuned project** and verify
it end to end. The contract is a **faithful 1:1 port**: one craft function →
one Intuned `automation` API, re-fitted only at Intuned's boundary.

## Prerequisites
- The Intuned CLI is installed and authenticated (`intuned auth whoami` shows a
  workspace). The skill never logs the user in or creates accounts.
- Input is a Webwright **craft output directory** (contains `final_script.py`
  with an `argparse` wrapper, `plan.md`, `task.json`). If it isn't, stop and say so.

## Read first
1. `transformation-rules.md` — the step-by-step transform and gates.
2. `intuned-contract.md` — the exact target (API signature, SDK, CLI,
   manifest), all verified against real scaffolds.
3. `gotchas.md` — the hardening layer. **Re-read before every port and
   add to it after every failure.**
4. `CONTEXT.md` — canonical vocabulary. `DECISIONS.md` — why the key decisions hold.

## Workflow (one port)
1. **Validate** the input is a real craft; else fail loudly.
2. **Scaffold** `intuned dev init <task_id> --template <python-starter | python-starter-auth>
   --language python --install-deps --non-interactive [--stealth]` into
   `intuned_projects/<task_id>/`.
3. **Transform** per `transformation-rules.md`:
   - strip the browser bootstrap + `asyncio.run` wrapper; the inner async body
     becomes `async def automation(page, params=None, **_kwargs)`;
   - map surviving params (snake_case preserved, harness params dropped+logged)
     into `Params`, a pydantic schema if needed, and `.parameters/.../default.json`
     so empty params reproduce the task;
   - replace `page.goto` → `go_to_url`; drop screenshots/file-writes; `log()`→`print()`;
     return substantive data minus harness fields;
   - set `apiAccess.enabled: true` and the Playground default input in `Intuned.jsonc`.
4. **Local gate:** `intuned dev run api <name> '{}'`; compare output to the craft's
   `final_runs/` known-good shape/count. (Protected site: a block is expected —
   don't fight it locally.)
5. **Deploy:** `intuned dev deploy --non-interactive` (after the local gate).
6. **Platform run (final gate):** `intuned platform runs start '{"api":"<name>","parameters":{}}'
   -p <task_id>`; poll `intuned platform runs get <id>` until terminal.
7. On any failure, root-cause into a `gotchas.md` entry, fix, re-run.

## Exceptions to faithful-port (decide deliberately)
- **Auth craft → AuthSessions** (DECISIONS.md §2): decompose login into
  `auth-sessions/create.py` + a derived `check.py`, enable `authSessions`; the
  `automation` assumes a valid session. Test with `dev run authsession create`
  then `--auth-session`.
- **Protected site** (DECISIONS.md §3): headful + stealth in the manifest; the deployed
  platform run is the only real gate. **Expected-rejection** tasks (LinkedIn) get
  no stealth — a clean reported rejection is the pass.
- **No crawl fan-out** by default — a crawl returns a flat list from one API;
  `extend_payload` is opt-in only.

## Guardrails
- Never launch a browser in `automation` (page is injected).
- Never invent Intuned APIs the craft didn't imply; this is a port, not a rewrite.
- Deploy goes to the user's own workspace — surface which workspace before first deploy.
- Don't try to beat bot-detection locally; that's what the deployed run is for.
