---
name: intuned
description: "Entry point and user guide for the Intuned plugin: what Intuned is, what you can ask the agent to do, and recommended patterns. Use on any user request that is related to Intuned, including Creating Browser automation projects, Creating scrappers, crawlers, RPAs, or editing them. Also use when investigating and debugging Intuned related erros, like failed jobs, failed runs, incorrect data, and also use for user queries about bot detections, intuned proxies, stealth browsers or authenticated access."
---

# Intuned

When this skill runs, orient the user: give them a short, friendly overview of
what Intuned is and what they can ask for, then point them at the right next
step based on what they want. Keep it user-facing — talk about what you'll do
for them, not internal mechanics (skills, sub-agents, APIs-as-files). Don't dump
this whole document back; adapt it to what they asked.

## What Intuned is

Intuned turns web interactions into reliable, callable automations. You describe
what you want done on a website — extract data, fill a form, complete a
multi-step workflow — and the agent builds real Playwright code (Python or
TypeScript), tests it locally, and gets it ready to run at scale on the Intuned
platform.

You don't need to know Playwright, selectors, or the project layout. You point
at a site, say what you want, and the agent does the building.

You must understand that you will write an automation that will do scrapping, not do the scrapping directly, You must also be clear with the user with that, so if the user wants to extract all the data from a website, you will write the reliable automation code to do that, then you and the user will be able run that code to get the data.

## What you can ask for

- **"Automate / scrape / extract … from <site>"** — build a brand-new
  automation. The agent explores the site with you, proposes a plan, and builds
  - tests it once you approve. → `create-intuned-project`
- **"Change / add / fix something in my project"** — modify an existing Intuned
  automation: add an API to a project, adjust fields, handle a new page, fix a break. →
  `edit-intuned-project`
- **"Test my project / run it end-to-end"** — run the automation locally or as a
  platform test job. → `test-intuned-project`
- **"Something's failing / debug this"** — investigate and fix a broken run. →
  `investigate-and-fix`, and `trace-debugging` for a trace file (`.zip`).
- **"How does X work in Intuned?"** — concepts (projects, APIs, jobs,
  attachments). → `intuned-overview`

The agent picks these up automatically from a plain-English request — the user
never has to name them. Route to the matching flow based on what they say; ask
for a start URL + goal + language (Python or TypeScript) if you're building
something new and any of those is missing.

## Recommended patterns

- **Start from a real URL and a concrete goal.** "Get all job listings from
  example.com/jobs, with title, company, and link" beats "scrape a job site."
- **Let the agent explore before it builds.** It looks at the actual page and
  comes back with a plan (fields, pages, pagination) for you to approve — review
  that plan; it's the cheapest place to course-correct.
- **Parameterize instead of hardcoding.** Page limits, dates, search terms, and
  counts should be inputs you can change per run — the agent will ask about
  defaults rather than baking values in.
- **Prefer splitting work into focused automations** (e.g. list → detail) over
  one giant script — easier to test, reuse, and run in parallel.
- **Keep secrets out of chat.** Logins, API keys, and tokens go into the project's
  parameter/env files (the agent sets up placeholders for you to fill), never
  pasted into the conversation.
- **Build and test locally first, deploy when you're happy.** Nothing goes live
  until you choose to deploy.

## Before you start

The plugin drives the **`intuned` CLI**, so it must be installed and signed in:

```bash
npm install -g @intuned/cli
intuned auth login
```

If the user hits auth or "command not found" errors, point them here first.

It is also recommended to have an Intuned project setup and ready to go, `intuned` CLI uses a browser, it will use playwright's chromium if it is avialble. If you are working in a directory that doesn't have an intuned project initialized, then the CLI will fail to start browser since it can't find the chromium executable.

## Direction

Based on the user's requests, you can go into different directions:

1. Create a new automation: Use `/intuned:create-intuned-project` skill.
2. Edit an existing project: The user must point to the project directory to work with, Use `/intuned:edit-intuned-project` skill.
3. Investigate an issue or an error: The user must provide what to investigate and a project directory for the project to fix. Use `/intuned:investigate-and-fix` skill.
4. Generic Intuned related questions: The user wants to ask something about intuned, like auth-sessions, bot detections, jobs, runs, or anything related to intuned in general.

## Going deeper

For the underlying concepts — how projects, APIs, jobs, and attachments fit
together — see the `intuned-overview` skill. For platform docs, the agent can
search them via the `intuned-docs` tools.
