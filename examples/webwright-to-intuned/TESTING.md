# Testing the skill with these examples

How to dogfood the `webwright-to-intuned` skill: port each example craft, then
verify the produced Intuned project reproduces the craft's known-good output. The
craft's `final_runs/` holds that known-good output to check against.

## Prerequisites
- Intuned CLI installed and authenticated: `intuned auth whoami` shows a workspace.
  (If `intuned` isn't found: `npm i -g @intuned/cli`.)
- The `webwright-to-intuned` skill available to your agent (`npx skills add
  Intuned/skills`), or this repo checked out so the agent can read the skill.

## The loop (per example)
1. **Port it.** Ask the agent:
   ```
   Port the Webwright craft in examples/<group>/<name>/craft to Intuned
   ```
   The skill scaffolds an Intuned project and writes `api/<name>.py` (it chooses
   `<name>`). Auth crafts also get `auth-sessions/create.py` + `check.py`.
2. **Local gate.** Run the ported API with empty params (the defaults must
   reproduce the task):
   ```
   intuned dev run api <name> '{}'
   ```
   For the **auth** example, create a session first, then run against it:
   ```
   intuned dev run authsession create '{"email":"demo@email.com","password":"DemoUser2024!"}' --id test
   intuned dev run api <name> '{}' --auth-session test
   ```
3. **Compare** the returned output to the craft's `final_runs/` known-good — same
   shape and (for deterministic sites) same count. See the table below.
4. **Deploy gate (optional, full verification).** Only after the local gate:
   ```
   intuned dev deploy --non-interactive
   intuned platform runs start '{"api":"<name>","parameters":{}}' -p <task_id>
   intuned platform runs get <run-id>     # poll until terminal
   ```
   A `SUCCEEDED` run with the same output is the real gate.

## Expected results

| Example | Site | Deterministic? | Pass looks like |
|---|---|---|---|
| `sandbox/pdf-crawl` | Intuned sandbox | ✅ stable | dict with `total_count: 2` and 2 PDF records (URL + product) |
| `sandbox/login` | Intuned sandbox | ✅ stable | 10 authenticated rows (7 columns: Id, Name, Supplier…) |
| `real/techcrunch-startup-news` | TechCrunch | ⚠️ date-dependent | `{ count, items, days_back: 7, … }`; item count varies by run date (was 22 at capture) — judge **shape**, not exact count |
| `real/books-discover` | books.toscrape.com | ✅ stable | `total_count: 1000` across 50 catalogue pages, de-duplicated URLs |

The two sandbox crawls and `books-discover` (a static demo site) are
reproducible — counts should match exactly. TechCrunch is live news, so the count
drifts with the date; verify the **structure and that it returns recent items**,
not a fixed number.

## What each example checks
- **pdf-crawl** — the default faithful 1:1 port (pagination + table extraction
  preserved; boundary swapped to `go_to_url` and a returned result).
- **login** — the AuthSessions exception: inline login decomposed into
  `create.py` + a derived `check.py`, with the API running already-authenticated.
- **techcrunch** — parameter mapping (`days_back`, `category_url` survive as typed
  params; the harness-only `output_filename` is dropped).
- **books-discover** — a crawl over full real-site pagination returned as one flat
  de-duplicated list (no fan-out).

## Cleanup
Deployed test projects and auth sessions live in your Intuned workspace. The CLI
has no project-delete; remove deployed test projects (and any leftover auth
session) from the workspace UI at app.intuned.io when you're done.
