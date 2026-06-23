---
name: self-healing
user-invocable: false
description: "Concept reference for Intuned self-healing, advanced-monitoring and project Issues — what an Issue is, how the platform raises and groups them from run anomalies, the issue record fields, the dismiss-vs-re-raise lifecycle, and the platform auto-fix/auto-merge/auto-deploy toggles. Load when working with a project's Issues (e.g. the fix-open-issues or investigate-and-fix flows) to understand where issues come from and what 'resolved' actually means, and when working with Intuned'd advanced monitoring feature."
---

# Self-Healing Projects and Issues

Background concept for the `fix-open-issues` skill. Full docs:
<https://intunedhq.com/docs/main/02-intuned-agent/self-healing-projects>

## What an Issue is

An **Issue** is a confirmed problem on a deployed project, they are raised on Job run errors, unexpected results, reduced result size, or an increase on error rate. The platform reaches it through a pipeline:

1. **Monitoring** — after each job run or standalone run, the platform captures metrics: **success rate, failure count, run count, and result size**, and checks them against anomaly-detection rules and historical data.
2. **Triage** — when an anomaly fires, the agent investigates it (reading healthy and failed runs, traces, and logs) and decides whether it's a **real issue or a false positive**.
3. **Surfacing** — confirmed issues with the **same root cause are grouped** and shown in the project's **Issues panel**.

## The issue record

`intuned platform issues get <issue-ref> --json` returns:

- **name** — short title.
- **explanation** — a brief, high-level description of _what_ looks wrong and roughly _where_. It has a description of the issue.

## Lifecycle — fixed, dismissed, re-raised

- Issues are **OPEN** when surfaced.
- You clear an issue by **dismissing** it — with the CLI (`intuned platform issues dismiss <issue-refs...>`) or the **"Dismiss"** button in the platform Issues panel. This applies both to false positives and to issues you've fixed.
- **Dismissing is not fixing** — it only removes the issue from the open list. If the root cause is still there, monitoring **re-raises** the issue on the next job runs.

## Platform auto-healing toggles

On the platform, self-healing can run hands-off via these settings:

| Toggle                  | What it does                                                                  |
| ----------------------- | ----------------------------------------------------------------------------- |
| **Advanced monitoring** | Automatically detect and surface issues from runs.                            |
| **Auto-fix**            | Automatically open an agent session to fix raised issues **on a new branch**. |
| **Auto-merge fixes**    | Automatically merge fix branches.                                             |
| **Auto-deploy fixes**   | Automatically deploy the project after a fix branch is merged.                |

In the UI a user can also **attach an issue to a message** — reference it in the agent input to start a conversation, and the agent loads the issue context and begins investigating.

`fix-open-issues` is the **manual, CLI-side equivalent of Auto-fix**: it does the discovery → triage → investigate → fix that Auto-fix automates, but it stops at a **deploy gate** so the user owns the deploy (the equivalent of Auto-merge / Auto-deploy) instead of it happening automatically.

## Enabling Advanced monitoring

You can enable the advanced monitoring feature to automatically detect Issues from job runs or standalone runs by running this command:

```bash
intuned platform project advanced-monitoring enable
```

This will setup the advance-monitoring feature on your project, So from now any run with failing metrics will raise an Issue.
