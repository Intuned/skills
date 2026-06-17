---
name: investigate-and-fix
description: "Investigate and fix a broken Intuned project. Use when the user reports something failing or returning wrong data, or gives a Run ID, Job Run ID, Issue ID, or free-text symptom. Pulls platform data, reproduces locally, diagnoses, fixes, and tests."
---

# Investigate and Fix

Debug and fix broken Intuned browser automation projects. You start from symptoms — something is broken, wrong, or unexpected — and your job is to diagnose the root cause and fix it.

---

## Entry Point: Identify the Input

The input to this skill can be one of four types. Identify it first:

| Type                  | Format                                                  |
| --------------------- | ------------------------------------------------------- |
| **Run ID**            | Can start with `ru_` or a short alphanumeric+dash token |
| **Job Run ID**        | UUID (8-4-4-4-12 hex), or starts with `jr_`             |
| **Issue ID**          | `Issue-` followed by a number (e.g. `Issue-42`)         |
| **Free-text request** | Natural language describing a failure                   |

Once you identify the type, use the matching lookup command below to retrieve the full context:

- **Issue ID / Multiple Issue IDs** → follow the **[Handling Issues](#handling-issues)** section (it has its own dedicated steps)
- **All other types** → jump to **Step 3: Reproduce Locally** after fetching the context below

### Run ID → fetch run details

```bash
intunedctl platform runs get <run-id> -p <project-name>
```

From the result you can read: API name, parameters, attempt count, error message, proxy. Then fetch attempt details:

```bash
# Get details for the latest (or a specific) attempt
intunedctl platform attempts get <run-id> [attempt-number] -p <project-name> --json

# Download logs for the attempt
intunedctl platform attempts log <run-id> [attempt-number] -p <project-name>

# Download Playwright trace for the attempt
intunedctl platform attempts trace <run-id> [attempt-number] -p <project-name>
```

### Job Run ID → fetch job run details

```bash
intunedctl platform jobruns get <job-run-id> -p <project-name> --json
```

The owning job is resolved automatically from the run ID — no need to look it up first.

From the result you can read: job configuration snapshot, proxy URL, successful/failed run counts. **Note:** `jobruns get` does not return individual run IDs. You must explicitly list them:

```bash
# List all runs belonging to this job run
intunedctl platform runs list -p <project-name> -f "job_run_id=<job-run-id>"
```

Then follow up with `runs get` / `attempts get` for each failing run ID returned above.

### Issue ID → fetch issue details

```bash
intunedctl platform issues get <issue-ref> -p <project-name> --json
```

From the result you can read: issue explanation, affected API, linked run IDs, parameters. Follow up with `runs get` / `attempts get` on the linked run IDs.

```bash
# List all open issues in the project
intunedctl platform issues list -p <project-name>
```

### Free-text request → check recent runs & issues first

```bash
# List recent runs (filter by status if needed)
intunedctl platform runs list -p <project-name> -f "status=FAILED" -f "job_run_id=jr_...."

# List open issues
intunedctl platform issues list -p <project-name>
```

Pick the most relevant failing run or issue, then use the corresponding `get` commands above to gather full context.

---

## Workflow

Follow this workflow in order. Every step matters — don't skip ahead.

### Step 1: Understand the Project

Read the user's description carefully. Then check the existing project:

- `README.md` — purpose
- `Intuned.json` — config
- `api/` — read the relevant API code
- `.parameters/api/<name>/default.json` — test params

If `Intuned.json` has `authSessions.enabled: true` or you see `auth-sessions/` API files, **immediately load the `auth-sessions` skill** before proceeding.

This skill assumes the project is already **provisioned and deployed** (that's how it has platform Runs/Issues to investigate). If `Intuned.json` has no `projectName` and platform lookups fail, the project was never provisioned — tell the user it needs `intunedctl dev provision` first, and work from the local code/symptoms instead.

Check if the Run/Jobrun had a Proxy configured.

Identify which API is affected and what the expected vs actual behavior is.

### Step 2: Check Platform Data

Use the commands from the **Entry Point** section above to retrieve run/job run/issue details. Collect:

- API name and parameters
- Error message and attempt count
- Proxy configuration (see table below)
- Playwright trace and logs

**Note:** The `-p` option for project flag is optional if the project is already set in `Intuned.json`.
You must confirm if `Intuned.json` has "projectName" or not. If it doesn't, then all `intunedctl platform` commands should be used with `-p`.

**Important**: When checking older runs or investigating multiple job runs, do not rely on successful, failed, or total run counts. There can be silent errors. Look into the logs and Playwright traces directly and give an accurate response based on facts — not assumptions based on dates, run counts, or day of execution.

**Proxy in run data:** Each command exposes the proxy differently — check the right field depending on which command you ran:

| Command       | Proxy location                         | Format                                    |
| ------------- | -------------------------------------- | ----------------------------------------- |
| `runs get`    | `input.proxy`                          | `{ server, username, password }` — values |
| `jobruns get` | `job_configuration_snapshot.proxy.url` | Full URL string                           |
| `jobs get`    | `proxy`                                | Full URL string                           |

Examples:

```json
// runs get → input.proxy (values may be partially redacted)
"proxy": { "server": "http://domain:port", "username": "username", "password": "password" }

// jobruns get → job_configuration_snapshot.proxy.url (always full URL)
"proxy": { "url": "http://username:password@domain:port", "version": "v1" }

// jobs get → proxy (always full URL)
"proxy": "http://username:password@domain:port"
```

**IMPORTANT:**
If a proxy is present in any of these fields, the run executed with a proxy. You must apply the same proxy to your investigation and reproduction steps.
Even if there was no Proxy in Intuned settings, as long as the Run had the proxy, then it ran with it and you must use that proxy in your work.

### Step 2.5: Check for Non-Fixable Errors

After fetching run and attempt details, check the **attempt-level** error codes. Run-level error codes like `api-attempts-failed` or `all-attempts-failed` are just wrappers — always look at the individual attempt errors to understand the actual problem.

To inspect the attempt error, run:

```bash
intunedctl platform attempts get <run-id> [attempt-number] -p <project-name> --json
```

The error code is at `error.code` and the documentation URL is at `error.doc_url` in the command output.

#### Memory-related

`script-process-crashed` repeated across all 3 attempts is almost always OOM — treat it as fixable. Load the `platform-errors` skill and follow its "Out of Memory" remediation. Skip Step 3 (local reproduction) — `intunedctl dev attempt api` runs outside the platform's memory cap and proves nothing about OOM. **Validation requires `intunedctl dev test-job`** at the original failing scale; a local run alone never qualifies. Always invoke the `test-intuned-project` skill before running `intunedctl dev test-job`.

#### Platform-level — not something a code fix can resolve

The following error codes are platform-level:

- `internal-server-error`
- `script-unexpected-error`
- `script-no-valid-output-received`
- `unexpected`
- `onepassword-integration-error`

When all attempts have one of these codes, skip reproduction and code fixes. Instead, respond to the user with:

1. An explanation of what the error means and what likely caused it (use the error message and your understanding of the error type)
2. What they should do next
3. A link to the error documentation page — use `error.doc_url` from the attempt output, or fall back to `https://intunedhq.com/docs/main/05-references/error-codes`
4. A suggestion to contact Intuned support

If the attempts have a **mix** of fixable and non-fixable errors, investigate the fixable ones normally and explain the non-fixable ones.

If the error code is **not** in the lists above (e.g. `script-execution-exception`, `script-timeout`, `result-too-big-error`, `auth-check-failed`), proceed with the normal workflow below.

### Step 3: Reproduce Locally

**REQUIRED — DO NOT SKIP: Proxy Gate**

Before running anything locally, check whether the run data from Step 2 contained a proxy.

**If a proxy was present in the run data → you must set it now before proceeding. This is not optional.**

Without the proxy, your local results are meaningless — they do not reflect real-world conditions. The site may behave completely differently (different content, no bot detection, no geo restrictions, different responses). Any conclusion you draw without the proxy is invalid.

**You cannot move forward with reproduction or testing until the proxy is set.**

Load the `proxy` skill, then set it:

```bash
intunedctl dev proxy set "<proxy-url>"
```

Only after confirming the proxy is active should you proceed.

Run the failing API locally with trace enabled:

```bash
intunedctl dev attempt api <api-name> .parameters/api/<api-name>/default.json --trace --cdp-browser-name "default" --cdp-tab-id <tab_id>
```

Use the Bash tool to run the command and set the `timeout` to at least `600000` (10 min). If it exits with code `143`, call `extendTimeout` inside the API code and increase the Bash `timeout`.

- If the error **reproduces**: proceed to diagnosis
- If the error **does NOT reproduce**: the issue may be environment-specific (network, timing, session state). Note this and analyze the platform traces from Step 2

### Step 4: Diagnose

Analyze all available evidence:

1. **Playwright trace** — invoke `trace-debugging` skill to analyze the trace file
2. **JSONL logs** — look for error patterns, timing issues, request failures
3. **The API source code** — understand the implementation and where it breaks
4. **The browser** — if needed, navigate to the site yourself to verify page structure has changed

#### Intuned Platform Errors

If the error matches a known platform error (Execution Timeout, CAPTCHA Solving Timeout, Out of Memory, Result Too Big), load the `platform-errors` skill for detailed causes, solutions, and how to identify each error in traces.

If the issue is auth-related (login failures, expired sessions, credential errors), load the `auth-sessions` skill. For deployed projects, also check the platform auth session state using `intunedctl platform authsessions` commands — the session may be expired, missing, or not yet created on the platform. The `intunedctl` skill's `platform authsessions` reference has the full command set and debugging workflow.

If the failure is a missing or wrong secret/config value (a missing API key, token, or endpoint), check the project's environment variables — see the `manage-env-vars` skill. Remember a platform var must include `AUTHORING` to be visible to local `dev attempt`/`dev run`.

If errors suggest network restrictions or IP-based blocking (e.g. navigation timeouts, `ERR_NETWORK_ACCESS_DENIED`, unreachable pages), see the **Bot Detection, CAPTCHA, and Proxy** section below and read the `bot-detection` skill for the proxy resolution flow.

Connect all findings to identify the root cause.

### Step 5: Fix

#### Use plan mode for complex fixes

If the fix is **complex** — it needs site exploration, new selectors, or a significant rewrite of the automation — **plan it first**: lay out the root cause and the proposed change, get the user's approval, then implement. Use your environment's plan mode if it has one; otherwise present the plan in chat and wait for the user to approve or ask for changes. For a small, well-understood fix (a logic bug, a wrong variable, a timing tweak), skip planning and fix directly.

#### If you're unsure about the fix

Present your findings and proposed fix with a direct proposal: "Found it — X is broken because Y. I'll fix it by doing Z." (fix it / wait, let me explain / show me more details).

If you're confident about the root cause and the fix is straightforward, go ahead and implement it directly — unless the fix is user-owned (cost/billing, API contract, dropped functionality).

#### When to Use Capability Skills

For data-source and API work, lean on the capabilities — don't hand-write selectors, network calls, or API code:

- **Broken or new selectors** → `build-selectors` (more robust across pages than by hand).
- **A broken or changed backend request** → `find-network-requests` (when the data comes from an XHR/fetch/GraphQL endpoint rather than the DOM).
- **Data source + significant code changes** → work out the data source (`build-selectors` / `find-network-requests`), then `implement-api`.
- **Browser automation code changes** (no new selectors/request) → `implement-api` for complex rewrites; for smaller edits, fix directly.
- **Small code-only fix** (logic bug, timing issue, wrong variable) → fix directly, no capabilities needed.

For a substantial fix, run the data-source step and `implement-api` in a sub-agent: tell it which capabilities to load, and pass the API name/path, the root cause, the URL(s) where it broke (or where you saw the request), and a browser tab id. Have it report what it found and test the fix locally. For a small one-line fix, edit directly.

### Step 6: Implement

Make minimal, focused changes. Fix the root cause — don't refactor surrounding code.

For a small fix you edit directly, load the `intuned-browser` skill for the available helpers and Playwright best practices (prefer intuned helpers like `go_to_url` and `wait_for_network_settled` over raw Playwright); for substantial code changes let `implement-api` handle it.

### Step 7: Test

Re-run the API locally with trace enabled:

```bash
intunedctl dev attempt api <api-name> .parameters/api/<api-name>/default.json --trace --cdp-browser-name "default" --cdp-tab-id <tab_id>
```

Use the Bash tool to run the command and set the `timeout` to at least `600000` (10 min). If it exits with code `143`, call `extendTimeout` inside the API code and increase the Bash `timeout`.

If the run **fails again**: analyze the new trace, iterate on the fix.
If the run **succeeds**: confirm with the user.

---

## Working With the User

**Be direct.** Lead with findings, not questions. Ask a specific question only when you need the user to decide.

### Asking Questions

Only ask when you need clarification — ground the question in what you found and offer clear options. Don't ask abstract questions.

### Bot Detection, CAPTCHA, and Proxy

If the failure is caused by bot detection or a CAPTCHA challenge, always check `Intuned.json` first to see what's already configured. Then read the **`bot-detection`** skill and follow its procedure for the full priority order.

> **Note:** stealth mode and the CAPTCHA solver are configured in `Intuned.json` (and the solver's code helpers) and only engage on a deployed run — there's nothing to enable or test locally. Locally, the lever that works is a normal user-supplied proxy (`intunedctl dev proxy set <url>` — see the `proxy` skill). If the original run used a proxy, you must already have it set from the Proxy Gate in Step 3.

---

## Handling Issues

### Issue ID format

`Issue-[number]` — for example, `Issue-42`. Multiple issues can be passed as a comma-separated list: `Issue-42, Issue-43, Issue-44`.

### Multiple Issues

When given more than one issue, work through all of them — fully resolve each one by following Steps 1–3 below. At the start, list all the issues you received and understand them very well.

### Step 1: Read the Issue

```bash
intunedctl platform issues get <issue-id> -p <project-name> --json
```

The issue record contains:

- **name** — A short title for the issue.
- **explanation** — A brief, high-level description of the problem for the user. It is **not** a root-cause analysis, **not** a suggested fix, and **not** a substitute for your own investigation.

Treat the title and explanation as orientation only: they tell you _that_ something is wrong and roughly _where_ in the automation it shows up. **You** must determine root cause and remediation by investigating.

### Step 2: Investigate

**You are responsible for finding root cause.** Use runs, logs, and traces — do not skip this step because the explanation sounds sufficient.

Use linked run IDs (when present) and any paths the explanation implies to gather evidence:

```bash
intunedctl platform runs get <run-id> -p <project-name>
intunedctl platform attempts log <run-id> [attempt-number] -p <project-name>
intunedctl platform attempts trace <run-id> [attempt-number] -p <project-name>
```

Read logs and traces systematically until you can explain _why_ the failure occurred and what change will fix it. The issue text does not contain that answer for you.

### Step 3: Fix

Follow the standard workflow — **Step 3: Reproduce Locally** through **Step 7: Test** — using the affected API name and parameters from the issue (and from what you learned in Step 2).

Validate your fix locally (including proxy requirements elsewhere in this skill) before treating the issue as resolved.

---

## Finishing Up

After successfully fixing the issue or making a code change, end with a concise plain-text chat summary:

- **Lead with the root cause** — what was broken and why.
- **State the fix** — what you changed and which API/files it touched.
- **Flag anything unresolved** or any limitation.
- **No jargon** — no selectors, no internal process details.

To ship the fix to the platform, deploy with `intunedctl dev deploy`. Mention this as the next step if the user wants it live. Skip the summary for rejected tasks, non-fixable platform errors, or failures where no code was changed.

## Rules Summary

1. **Diagnose first, fix second** — understand the root cause before touching code
2. **Check platform data** — traces and logs tell you what actually happened
3. **Reproduce before fixing** — confirm the issue locally when possible. **If the run had a proxy, you MUST set it before any local reproduction or testing. Results without the proxy are invalid and do not reflect real-world conditions.**
4. **Minimal fixes** — fix the root cause, don't refactor surrounding code
5. **Test your fix** — re-run the API at least once
6. **End with a chat summary** — concise plain-text recap; deploy via `intunedctl dev deploy`

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
