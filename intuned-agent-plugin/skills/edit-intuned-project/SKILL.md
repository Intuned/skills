---
name: edit-intuned-project
description: "Add, change, or extend APIs in an existing local Intuned project. Must Use whenever working on an existing Intuned project, example: add a feature, change a schema, update selectors, fix an API, or edit Intuned.json/job config."
---

# Edit Intuned Project

Add, modify, or extend an existing Intuned browser automation project in the user's local repo. Explore the site yourself with the browser tools, pick the approach based on how big the change is, and use the capability skills (`build-selectors`, `implement-api`) for selector and API work — offloading them to sub-agents when the work is substantial (see "Implementation via Capability Skills").

The project is expected to already be **provisioned** on the platform (it exists in the repo). If `Intuned.json` has no `projectName`, the project was never provisioned — mention that platform commands and deploy need `intuned dev provision` first, and offer to run it. Changes are shipped with `intuned dev deploy`, which you **suggest at the end** (don't deploy unprompted).

If the user is requesting to create a complete new project, and not to make edits on the current project, then you must call `create-intuned-project` skill.

**Browser binary:**
You will work on a chromium browser, you will control it via intuned CLI, you must always read `browser-management` skill to understand how to work with the browser.

## Working With the User: CRITICAL RULES

**Investigate first, then come back with specifics.** Don't ask abstract questions — explore the site and code, then present concrete options and ask a specific question when you need the user to decide.

### Asking Questions

Only ask when you genuinely need to clarify, gather information, or weigh options — not just to ask. When you do, ground the question in something specific you found and offer clear choices so the user can decide quickly.

### The Loop: Investigate → Present → Decide Together

1. **Investigate** - Explore the site, read the code, understand what exists
2. **Present findings** - Show the user what you discovered with specifics
3. **Discuss options** - ask, with specific options based on findings
4. **Implement** - Only after agreement, make the changes
5. **Test** - Run the API to verify it works

**Example:** User asks to "add filtering"

```
WRONG: "What kind of filtering do you want?" (vague, no investigation)

RIGHT:
1. Navigate to the site, explore available filters
2. Ask: "Found 3 filters on the site: Category (12 options), Price Range, and In Stock. Which should I add?" (all three / category and price range / category only / let me specify)
3. User picks → you implement
```

**Example:** User asks to "add a new step to the form submission"

```
WRONG: "What step do you want to add?" (vague, no investigation)

RIGHT:
1. Navigate to the site, explore the current form workflow
2. Ask: "I see the form currently handles 3 steps. There's also a 'Review' step that appears after step 3. Want me to add that?" (yes, add the Review step / no, I meant something else / let me explain)
3. User picks → you implement
```

Every question should reference something specific you observed — and end with a clear choice.

### Before Implementing

Always confirm before writing code, with a direct proposal:

- **New features**: "The site has A, B, and C available. Which should I add?" (add A / add A and B / add all / something else)
- **Modifications**: "I can change X by doing Y — here's how it'll work." (do it / wait, let me explain / show me more details)

**CRITICAL:** Never implement without confirming first. Even obvious changes get a quick check.

## Getting Started

Check the existing project:

- `README.md` - purpose
- `Intuned.json` - config
- `api/` - existing APIs and patterns
- `.parameters/api/<name>/default.json` - test params

If `Intuned.json` has `authSessions.enabled: true` or you see `auth-sessions/` API files, **immediately load the `auth-sessions` skill** before proceeding.

The agent runs inside the project, so the project identity comes from `Intuned.json` (the `projectName` field) or the `--project-name` flag — there is nothing to select.

## Deciding Your Approach

**The key question: does this task require exploring the website?**

### Changes that need exploration → plan first

When the task **requires browser interaction** — exploring the site, building selectors, or writing automation logic that depends on page structure — plan it first: explore, lay out the change, and get the user's approval before implementing. If your environment has a plan mode, use it for this; if not, present the plan in chat and wait for the user to approve or ask for changes. Examples:

- Adding a new API (need to explore the site, build selectors, or document network requests)
- Adding new fields that require new selectors (need to locate elements on the page)
- Changing navigation logic (need to understand the site flow)
- Adding pagination or filtering support (need to explore how the site implements them)
- Major refactors that change how the automation interacts with the page

### Changes that don't → implement directly

When the change is purely code — no site exploration, no new selectors — skip the planning step and make it directly. Examples:

- Renaming a schema field
- Adding a field that's already extracted but not included in the schema
- Changing parameter defaults
- Code cleanup or refactoring that doesn't change page interaction

### Summary

| Needs browser?                        | Approach                                                                        |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| **No** — code-only change             | Read code → propose → **confirm with user** → implement → test                  |
| **Yes** — needs selectors/exploration | Plan first → explore site → present plan → **user approves** → implement → test |

**Every approach requires user confirmation before implementation.** Gather any inputs you need (like a URL or description) before you start planning.

## Investigating the Website

### CAPTCHA and Bot Detection Handling

If you encounter any bot detection signal (blocked page, CAPTCHA, Cloudflare, 403/429, Access Denied) — **stop, do not reject, do not continue exploring**. Read the **`bot-detection`** skill and follow its procedure — it owns the full priority order (stealth → captcha solver → proxy) and the exact commands.

> **Note:** stealth mode and the CAPTCHA solver are configured locally (in `Intuned.json`, plus the solver's code helpers) so they take effect once the project runs on the platform — they simply don't engage during local dev, so there's nothing to test locally. The `bot-detection` skill owns the config and the decision flow. For a block you need to get past _right now_ while working locally, a normal user-supplied proxy is the lever that works (see the `proxy` skill).

**You MUST explore the target website yourself using browser tools** (screenshot, scroll, `find`, `query_by_selector`). Do the exploration yourself in your main loop — don't delegate it. Selector-building and implementation are what you later offload to sub-agents, not the initial exploration.

Understand:

- Page structure and user flow
- What elements you'll need
- What elements and data are available

Don't write selectors here — building reliable selectors is the `build-selectors` skill's job (see below). This step is just exploration to plan the change.

## Implementation via Capability Skills

For data-source and API work, lean on these capabilities — don't hand-write selectors, network calls, or API code:

- **`build-selectors`** — finds elements and builds reliable selectors for a page.
- **`find-network-requests`** — identifies the backend request a page uses when its data comes from an XHR/fetch/GraphQL endpoint rather than the DOM.
- **`implement-api`** — writes (or edits) the API code using those findings.

Pick selectors, the network request, or both per API depending on where the data lives.

**Offload substantial work to a sub-agent.** When adding a new API or doing a complex change, have a sub-agent work out the data source (`build-selectors` and/or `find-network-requests`) and run `implement-api` — tell it which capabilities to load, and pass the API name/path, the relevant change/plan details verbatim, the URL(s) (every page the selectors must verify against, or where you saw the request), and a browser tab id. Have it report its findings and test the result locally. Independent APIs can run in parallel — give each sub-agent its own tab via `intuned dev browser tabs create` so they don't collide. For a small single-API tweak, doing it inline is fine.

### When to use them

- **Adding a new API** → work out the data source (`build-selectors` / `find-network-requests`), then `implement-api`. Don't write the API file by hand.
- **New selectors / network request / browser logic** (new pagination, navigation, major refactor) → use the matching capability — they're more robust and consistent than doing it by hand.
- **Code-only changes** (rename a field, change a default, fix a logic bug, cleanup) → just edit directly.

## Implementation

When you write or edit API code directly (a small inline change), let `implement-api` handle substantial work — load the `intuned-browser` skill for the available helpers and Playwright best practices (preferring intuned helpers like `go_to_url` and `wait_for_network_settled` over raw Playwright), and follow `implement-api` for how API files are structured.

## Editing Jobs

If the user asks to add, change, or remove a job (schedule, payload, configuration, proxy, etc.), read the files in the `intuned-resources/jobs/` directory and edit the relevant `.job.json` file directly.

> **Tip:** Code-origin Jobs are managed by editing the `*.job.json` file (then `intuned dev deploy`). API-origin Jobs are managed via `intuned platform jobs update | pause | resume | delete`. Exception: `pause` and `resume` work on either origin (operational toggles, not edits).

For the full job schema and workflow, load the `manage-jobs` skill.

---

## Intuned Project Related Edits

These are common project-level configuration changes made by editing `Intuned.json` in the project root. No browser exploration is needed — read the file, make the change, confirm with the user.

These edits may include:

- Enabling headful mode
- Setting up a proxy (normal user-supplied proxy: `intuned dev proxy set <url>` — see the `proxy` skill)
- Editing Replications
- Control deployed project region
- Configuring `stealthMode` / `captchaSolver` (see the `bot-detection` skill)
- Adding environment variables or secrets an API needs (see the `manage-env-vars` skill)

> **Stealth / CAPTCHA solver:** configure `stealthMode` / `captchaSolver` in `Intuned.json` (and the solver's code helpers) so they take effect once the project is deployed — they don't engage during local dev, so there's nothing to "enable" or test locally. The `bot-detection` skill owns this. A normal user-supplied proxy is the one anti-bot lever that also works locally.

For configuration syntax and the full field reference, load the `project-settings` skill.

---

## Testing

Refer to `test-intuned-project` skill.

Run the edited APIs locally to test your work with `intuned dev attempt api <name> <parameters_path>` (set `export MODE=generate_code` first — local testing mode that mocks file/attachment uploads; see `dev_attempt.md`).

Test your changes before completing. If something fails, use the trace file with the `trace-debugging` skill (read the trace directly).

For end-to-end platform testing (significant logic change, `extend_payload` chain behavior, sinks, or any OOM-prone code), invoke the `test-intuned-project` skill before running `intuned dev test-job`.

### Build verification (required)

After any code change — whether you wrote it yourself or `implement-api` did — run the project's type-check from the project root and fix any errors before completing:

- **TypeScript**: `npx tsc --noEmit`
- **Python** (run both; fix failures before proceeding):
  1. **Static types (Pyright)**: `uvx pyright --pythonpath "$(uv run which python)"`
  2. **Syntax / import graph**: `uv run python -m compileall . -x "\.venv" -q`

Re-run until it passes. Never skip this step, even for small edits.

## Finishing Up

After successfully completing the task or making a code change, end with a concise plain-text chat summary:

- **Lead with the result** — what you changed and which APIs/files it touched.
- **Flag anything that didn't work** or any limitation (e.g. a partially blocked site).
- **No jargon** — no selectors, no internal process details.

To ship the changes to the platform, deploy with `intuned dev deploy`. Mention this as the next step if the user wants the changes live. Skip the summary for rejected tasks or failures where no code was changed.

## Rules Summary

1. **Explore first, discuss second** — explore the site/code, then present findings to the user
2. **Ground questions in observations** — never ask abstract questions, reference what you found
3. **Ground questions in what you found** — offer clear options so the user can decide quickly
4. **Decide together, then implement** — user chooses from options you discovered
5. **Explore the site yourself** — do exploration in your main loop; offload selector-building and implementation to sub-agents for substantial work
6. **All selectors from build tools** — never write selectors manually; use the `build-selectors` skill
7. **Test your changes** — run the API at least once
8. **End with a chat summary** — concise plain-text recap; deploy via `intuned dev deploy`

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
