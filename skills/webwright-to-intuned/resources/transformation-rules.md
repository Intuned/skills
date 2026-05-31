# Transformation rules: Crafted CLI → Intuned API

The input is a Webwright **craft output directory**: `final_script.py` (logic
source), `plan.md` (authoritative `# Parameters` table), `task.json` (task text +
`start_url`), and `final_runs/run_NNN/` (known-good output to verify against).
Assume the craft already ran green — this skill translates, it does not debug
Webwright. If `final_script.py`, its `argparse` wrapper, or `plan.md` is missing,
**fail loudly**: this is not a craft.

## 1. Names

- Project name = `task.json.task_id` (kebab/snake as given).
- API name = the craft's domain (from the function name `scrape_<domain>` or the
  task) — a short, clean noun (`discover`, `crypto`, `compare`). File = `api/<name>.py`.

## 2. Parameters (the crux of "faithful")

- Source of truth = `plan.md`'s `# Parameters` table, cross-checked against the
  `argparse` flags and the function signature.
- **Preserve snake_case names verbatim.** No camelCase conversion.
- **Drop harness-only params** — anything whose purpose is local artifact I/O
  (`output_filename`, run-dir/screenshot/log paths, verification toggles). They
  have no meaning in Intuned (output is the return value). **Log every dropped
  param** so the decision is auditable.
- Build `class Params(TypedDict)` with one field per surviving param; add a
  pydantic schema in `utils/` if validation/coercion is non-trivial (use
  `plan.md`'s "allowed/format" column for validators).
- `.parameters/api/<name>/default.json` = the surviving params at their **craft
  defaults** (which equal the original concrete task). Mirror the same defaults
  into `Intuned.jsonc → metadata.defaultRunPlaygroundInput.parameters`.
- Invariant: `intuned dev run api <name> '{}'` must reproduce the original task,
  exactly as `python final_script.py` with no args did.

## 3. Browser lifecycle (mandatory strip)

Delete entirely — the platform owns the browser and injects `page`:
- `async with async_playwright() as p:` / `p.chromium.launch(...)`
- `browser.new_context(viewport=...)` / `context.new_page()` / `browser.close()`
- the outer `asyncio.run(_inner(...))` sync wrapper and the sync entry function
- the `headless=...` argument (manifest-controlled)

The craft's **inner async body** becomes the body of
`async def automation(page, params=None, **_kwargs)`, operating on the injected
`page`. Do **not** re-apply the craft's viewport (decided: skip).

## 4. Navigation

- Replace every `await page.goto(url, wait_until=..., timeout=...)` with
  `await go_to_url(page, url=url, timeout_s=<craft timeout or 15>, retries=3)`.
- Leave all other `page.*` interactions (locators, clicks, fills, evaluate)
  **verbatim** — that is the faithful logic.
- `wait_for_load_using_ai=False` by default (opt-in only).

## 5. Output & artifacts (mandatory strip)

- Return the craft's substantive data (`items`/list/dict + count + summary)
  **minus** harness/filesystem fields (`run_dir`, `output_path`, screenshot
  paths, `verification`). Return a plain dict/list — no pydantic *output* model.
- Drop all local writes: JSON dump, `verification.html`, step-log file, and
  every `page.screenshot(...)`. Intuned's traces/recordings replace them.
- Convert the craft's `log()` to plain `print()` for breadcrumbs.
- Use `save_file_to_s3` **only** when the deliverable is the binary itself
  (not for URL-listing tasks).
- Ensure the return is JSON-serializable (datetimes → ISO strings, etc.).

## 6. Exceptions to faithful-port

### 6a. Auth crafts → AuthSessions (DECISIONS.md §2)
A craft that logs in (fills a login form, then navigates to a protected page):
- Scaffold from `python-starter-auth` (or add the auth-sessions files).
- Move the login steps into `auth-sessions/create.py` `async def create(page, params)`;
  credentials → create params; `.parameters/auth-sessions/create/default.json` =
  the task creds.
- Derive `auth-sessions/check.py` `async def check(page) -> bool` using a
  logged-in-only signal (an element that exists only when authenticated). **Verify
  this signal in the test loop — do not assume it.**
- `Intuned.jsonc`: `authSessions.enabled = true`, `type "API"`.
- `automation` keeps only the post-login work (assumes session applied).
- Test: `intuned dev run authsession create '{creds}' --id test` then
  `intuned dev run api <name> '{}' --auth-session test`.

### 6b. Bot-detection blocks → stealth + deployed gate (DECISIONS.md §3)
If a run is blocked by anti-bot defenses, don't conclude the port is broken:
stealth, captcha solving, and proxies run only on the deployed platform, never
under local `intuned dev run`. Set `headful: true` and `stealthMode.enabled: true`
in the manifest (init with `--stealth`) and verify via deploy +
`intuned platform runs start`. Add `captchaSolver` (needs headful+stealth) or a
per-run `proxy` only if the deployed run is still walled. Configure per the docs:
https://intunedhq.com/docs/main/02-features/stealth-mode-captcha-solving-proxies

## 7. Pipeline & gates (one port)

1. Validate input is a real craft (else fail loud).
2. `intuned dev init <task_id> --template <python-starter|python-starter-auth> --language python --install-deps --non-interactive`.
   (No `--stealth` by default — it's reactive; add it only after an observed block, per rule 6b.)
3. Transform per rules 1–6; write all files.
4. **Local gate:** `intuned dev run api <name> '{}'` (auth: create session first).
   Pass = output matches the craft's `final_runs/` known-good shape/count.
   If the run is blocked by anti-bot defenses, don't pre-judge the site — a block
   isn't a port failure if the logic reached the wall; escalate via rule 6b.
5. **Deploy:** `intuned dev deploy --non-interactive` (gated on step 4).
6. **Platform run (final gate):** `intuned platform runs start '{"api":"<name>","parameters":{}}' -p <task_id>`
   → poll `intuned platform runs get <id>`. This deployed run is the real gate when a local run was blocked.
7. On any failure: root-cause → add a `gotchas.md` entry (symptom → cause → rule)
   → fix → re-run. Iterate until pass.
