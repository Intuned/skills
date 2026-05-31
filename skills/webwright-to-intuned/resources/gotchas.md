# Gotchas (living hardening layer)

Each entry: **Symptom → Cause → Rule**. Add one every time a port fails during
testing. Seeded from ground-truth scaffolding and extended across real porting runs.

---

## G1 — `automation` never launches a browser
**Symptom:** Two browsers open, or "browser already running", or the run hangs.
**Cause:** The craft's `async_playwright()` / `chromium.launch()` was copied in.
The platform injects `page`.
**Rule:** Strip the entire browser bootstrap and the `asyncio.run` wrapper. The
craft's inner async body becomes `automation`'s body using the injected `page`.

## G2 — Entry point must be exactly `automation`
**Symptom:** `intuned dev run api <name>` errors that no automation is found.
**Cause:** Left the craft's function name (`scrape_<domain>`).
**Rule:** Rename the entry coroutine to `automation(page, params=None, **_kwargs)`.
Keep helpers under their own names.

## G3 — Drop harness-only params
**Symptom:** Intuned params that do nothing (`output_filename`), or the port
writes files that vanish.
**Cause:** Faithfully copied Webwright artifact-I/O params.
**Rule:** Drop params whose purpose is local artifact I/O; log each drop. Output
is the return value, not a file.

## G4 — Default params must reproduce the task
**Symptom:** `intuned dev run api <name> '{}'` returns empty / wrong scope.
**Cause:** `.parameters/.../default.json` left as `{}` or with wrong defaults.
**Rule:** default.json (and `metadata.defaultRunPlaygroundInput.parameters`) =
the craft's concrete defaults, so empty-params reproduces the original task.

## G5 — Python 3.12 only
**Symptom:** `uv sync` resolution error or version conflict.
**Cause:** Edited `requires-python` or pulled deps needing other versions.
**Rule:** Keep `requires-python = ">=3.12,<3.13"`, `playwright==1.56`, and the
template's `intuned-runtime`/`intuned-browser` pins. Add task deps additively.

## G6 — Stealth/captcha are platform-only
**Symptom:** Local run blocked by anti-bot defenses; agent "fixes" it forever.
**Cause:** Expecting stealth/captcha to work under `intuned dev run`.
**Rule:** Stealth, captcha solving, and proxies run only on the deployed platform.
Don't burn local iterations trying to beat a wall — enable headful+stealth in the
manifest and verify via `intuned platform runs start`. (DECISIONS.md §3; docs:
https://intunedhq.com/docs/main/02-features/stealth-mode-captcha-solving-proxies)

## G7 — Return must be JSON-serializable
**Symptom:** Run fails serializing the result.
**Cause:** Returning `datetime`, `Path`, pydantic objects, etc.
**Rule:** Return plain dict/list; convert datetimes to ISO strings, paths to str.

## G8 — Navigation via `go_to_url`, not `page.goto`
**Symptom:** Flaky loads / premature scraping on slow pages.
**Cause:** Kept `page.goto` without reliable load waiting.
**Rule:** Replace `page.goto(url, ...)` with
`go_to_url(page, url=url, timeout_s=..., retries=3)`. Keep other `page.*` verbatim.

## G9 — `apiAccess.enabled` must be true for platform runs
**Symptom:** `platform runs start` rejected / API not callable after deploy.
**Cause:** Template default `apiAccess.enabled = false`.
**Rule:** Set `apiAccess.enabled = true` in `Intuned.jsonc` before deploy.

## G10 — Platform auth-session runs need a nested `authSession`, pre-created
**Symptom:** `platform runs start` → `400 ... Auth session is required for auth
session validation runs`.
**Cause:** Passed `authSessionId` at the top level, or didn't create the
platform session first. The run data field is a nested object.
**Rule:** First `intuned platform authsessions create <id> -p <project>
--input '{creds}' --wait`. Then start the run with
`{"api":"...","parameters":{...},"authSession":{"id":"<id>"}}`. (Alternatively
`"authSession":{"runtimeInput":{...creds}}` for runtime-based.)

## G11 — Don't edit `Intuned.jsonc` with regex/sed that eats `//`
**Symptom:** Corrupted manifest, or a JSON validator chokes on a URL line.
**Cause:** A naive `s|//.*||` comment-strip (or sed) also strips `//` inside
`https://` URLs in `defaultRunPlaygroundInput`/start URLs.
**Rule:** Edit `.jsonc` with exact string edits, not regex over `//`. To validate,
use a real jsonc parser, not `re.sub('//.*','')`.

## G12 — Platform run output is nested and async
**Symptom:** Parsing `dev run` shape against a `platform runs` result fails
(`KeyError`), or you read a pending run as "empty".
**Cause:** Local `dev run` prints the return value directly; a platform run wraps
it under `result.output` and is async.
**Rule:** Use `--wait` (or poll `platform runs get <id>`). The payload location
varies: `runs get` nests it at `result.output`, while `--wait` may put it at
`result` directly — read defensively (`result.output or result`). Status strings
are UPPERCASE (`SUCCEEDED`/`completed`) — match case-insensitively. `--json`
output is prefixed by progress lines; extract the JSON object before parsing.

## G13 — Strip ALL browser-provider bootstrap, not just local launch
**Symptom:** Port imports `httpx`, references `BROWSERBASE_API_KEY`, or calls
`connect_over_cdp`; or it adds deps the project doesn't need.
**Cause:** Some crafts carry an alternate provider block (e.g. Browserbase CDP
with `advancedStealth`) in addition to / instead of `chromium.launch`.
**Rule:** Remove every browser-provider path (local launch AND Browserbase/CDP)
and its imports. Intuned injects `page`; the port needs zero provider code.
For anti-detection use Intuned's `stealthMode`/proxy, never a craft's Browserbase.

## G14 — "Submitted" can be ambiguous; faithfulness = match the craft's verdict
**Symptom:** A form RPA returns `submitted=false`/"no confirmation" and looks broken.
**Cause:** The target may not render a clear confirmation; the craft's own
heuristic is the only available oracle.
**Rule:** Judge against the craft's known-good final run (Fork A). If all steps
execute (heading `wait_for`s pass) and the result matches the craft's final
verdict, it's a faithful pass — don't invent a confirmation the site never shows.
