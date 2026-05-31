---
description: Port a Webwright Crafted CLI into a deployed, verified Intuned project.
argument-hint: <path-to-craft-output-directory>
---

Operate as the `webwright-to-intuned` skill. Port the Webwright **Crafted CLI**
at the path below into a hosted Intuned project, end to end.

Craft output directory:

$ARGUMENTS

First read the skill's `SKILL.md` (the parent of this `commands/` folder), then
`reference/transformation-rules.md`, `reference/intuned-contract.md`, and
`reference/gotchas.md`. Then execute the full workflow:

1. Validate the path is a real craft (`final_script.py` + `argparse` + `plan.md`);
   if not, stop and report what's missing.
2. Confirm `intuned auth whoami` and state which workspace will receive the deploy.
3. Scaffold into `intuned_projects/<task_id>/`, transform per the rules
   (faithful 1:1 port; auth → AuthSessions; protected site → stealth + deployed
   gate), and write every file.
4. Local gate (`intuned dev run api <name> '{}'`) compared to the craft's
   `final_runs/` known-good output.
5. Deploy (`intuned dev deploy`), then verify a standalone run
   (`intuned platform runs start ... -p <task_id>` → poll `runs get`).
6. Record any failure as a `gotchas.md` entry (symptom → cause → rule), fix, re-run.

Report: the project path, the local-run result, the deploy status, and the
standalone platform-run output, plus any params that were dropped and why.
