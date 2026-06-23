---
name: fix-open-issues
description: "Sweep, triage, and fix all open issues on a deployed Intuned project. Use when the user wants to clear open issues: 'fix my open issues', 'what issues are open / what's broken on my project', 'resolve all my issues', 'self-heal my project', 'go through my issues and fix them', or 'run self-healing'. Discovers open issues from the platform, fixes them, then stops at a deploy gate and guides the rerun. For a single known Run/Job Run/Issue ID or free-text symptom, use investigate-and-fix instead."
---

# Fix Open Issues

Clear the **open issues** on a deployed Intuned project in one pass. You discover every open issue, triage which are actually fixable in code, fix each one, and then hand the user a clear summary with the deploy and rerun steps.

This is the manual, CLI-side equivalent of the platform's **Auto-fix**, except that you can keep control of the deploy and work with the user on the fix. Load the `self-healing` skill first to understand where issues come from and what "resolved" actually means.

This skill is an **orchestrator**. It does not contain its own diagnose/fix workflow — it discovers and triages issues, the actual investigating and fixing flows are in the `investigate-and-fix` skill, so you must read it at first to understand how investigting and fixing goes.

---

## Before you start

- **The project must be provisioned and deployed.** Issues only exist for deployed projects. If `Intuned.json` has no `projectName` and platform lookups fail, the project was never provisioned — tell the user and stop.
- **The project must have Self-healing enabled**: `intuned platform project get -p <project-name>` will return the project's information including Self-healing if it is enabled or not, it will also return the project's healing level, if it is enabled then it will be higher than 1 (at least detect issue is enabled).
- **Project name:** the `-p <project-name>` flag is optional when `Intuned.json` has `projectName`. Confirm it's there; if not, pass `-p` on every `intuned platform` command.

---

## Workflow

### 1. Understand self-healing

Load the **`self-healing`** skill to understand Intuned's self-healing feature.

### 2. Discover the open issues

```bash
intuned platform issues list -p <project-name>
```

If the list reaches the page limit (default 50), paginate with `-l`/`-o` so you capture **all** of them — don't fix a partial set silently.

- **No open issues** → tell the user the project is healthy and stop. Nothing to fix.
- **Otherwise** → list them back by ref + name so the user sees the full scope before you start.

### 3. Fix each fixable open issue

**load the `investigate-and-fix` skill and follow its _Handling Issues_ section**

You will have the issue-id for each issue, you apply the investigate-and-fix instructions on every issue.
Some issues may share the same root cause, you can fix one or multiple issues on 1 code change, so your job is resolve all issues all together.

Your job here is orchestration:

### 4. Deploy

Once every fixable issue's change is made and locally validated and tested, **stop**. Do **not** run `intuned dev deploy` on your own initiative.

Summarize the changes and ask the user how to proceed: deploy now, or hold. use AskUserQuestion to confirm with the user.

A. If the user doesn't approve the deployment. Then stop with a summary if what fixes were dont and that the issues are still open, and write a reminder to the user that the fix will not take effect until the project is deployed. And also tell the use that they can manually dimiss the issue from the Intuned platform UI at `https://app.intuned.io/projects/<id>` which will be on the right panel containing Issues liss, by clicking on "Dismiss" button. The deployment for the issues fix can only be done through CLI to capture the local changes, not through UI.

B. If the user approves the deployment:

1. Dismiss the resolved issues:

```bash
intuned platform issues dismiss <issue-1 issue-2 .... >
```

2. Deploy the project

```bash
intuned dev deploy
```

### 6. Guide what happens next

After deploy, set expectations — the fix is live, and self-healing confirms it on the next platform runs:

- **The change takes effect on the next runs.** Let the user know the deployed fix applies to upcoming job runs; self-healing re-checks each one, so if the root cause is fixed, the issue won't be raised again. (Surfacing is batched up to ~6h, so give it a little time before reading too much into it.)
- **Or run a job now to confirm sooner.** If the user doesn't want to wait, trigger one representative job run at the **original failing scale and parameters** — re-trigger the affected job (the `manage-jobs` skill / `intuned platform jobs`) or run an end-to-end test job (the `test-intuned-project` skill / `intuned dev test-job`) — and confirm it succeeds. For OOM and other platform-capped errors, validation must come from a platform run like this (or the next real job run), never a local `intuned dev attempt` (the `platform-errors` skill covers this).
- **If the issue keeps coming back, the fix didn't hold** — the root cause wasn't addressed (the Step 5 dismiss was premature). Loop back to Step 3 with the new run's logs and traces and re-investigate.

---

## Finishing up

End with a concise plain-text recap covering the whole sweep:

- **Per fixed issue** — the root cause, what you changed, and which API/files it touched. Lead with the root cause.
- **Next steps** — deploy status, and how to rerun to confirm (job re-trigger or `intuned dev test-job`), reminding them issues resolve on a healthy rerun, not on deploy.

Keep it jargon-free — no selectors or internal process details.

---

## Consulting the docs

For more on self-healing and issues, see <https://intunedhq.com/docs/main/02-intuned-agent/self-healing-projects> or search the Intuned docs with the `search_intuned` and `query_docs_filesystem_intuned` tools.
