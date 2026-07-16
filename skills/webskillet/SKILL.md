---
name: webskillet
description: "Webskillet runs web tasks described in plain English — scraping, form-filling, multi-step site automation — in a cloud browser agent and returns structured JSON. Use it whenever a task needs live data or actions on a real website."
---

# Webskillet

Webskillet is a web-task service: you describe what you want done on a website in plain English, and a cloud browser agent figures out how, does it, and returns the result as structured JSON. It can scrape listings and tables, extract data from pages, fill forms, and run multi-step flows — with no selectors or automation scripts to write.

## A task

The instruction (`task`) is the only required input. Everything else is optional and narrows or guides it:

- **`task`** (required) — the plain-English instruction.
- **`startUrl`** (optional) — where to begin; omit it and the agent finds the page itself.
- **`parameters`** (optional) — inputs that vary between runs (a search term, a date range) as structured values instead of edits to the task text.
- **`outputSchema`** (optional) — the JSON shape you want back; the result is validated against it.

A full task looks like this (the same example is used in every section below):

```json
{
  "task": "Extract the title and points of the top Hacker News stories",
  "startUrl": "https://news.ycombinator.com",
  "parameters": { "count": 5 },
  "outputSchema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "points": { "type": "number" }
      }
    }
  }
}
```

## Skillets — what makes Webskillet different

The first time Webskillet runs a task, it doesn't just return the result — it builds a reusable automation for that task (generated code plus what it learned about the site) and saves it as a **skillet**, returning the skillet's id alongside the result.

Pass that id on later runs and Webskillet executes the saved automation directly instead of figuring the task out from scratch — much faster and much cheaper. The skillet keeps getting better: successful runs save anything new it learned, and if the site changes and the code breaks, Webskillet repairs it mid-run and keeps the fix. A failed run never leaves a skillet worse than it started.

A skillet is a parameterized automation, not a recording of one run. The same skillet handles different URLs, parameter values, and phrasings of the same task — so reuse one id for each *kind* of task ("extract products from a category page"), and start a new id only for a genuinely different automation.

## CLI

The preferred way to use Webskillet. No API key needed — `auth login --browser` opens a browser login without prompting. `auth status` exits nonzero when not authenticated, so log in only when needed:

```bash
npx webskillet auth status || npx webskillet auth login --browser

# Start a run and wait for the result
npx webskillet run "Extract the title and points of the top Hacker News stories" \
  --start-url https://news.ycombinator.com \
  --parameters '{"count": 5}' \
  --output-schema '{"type":"array","items":{"type":"object","properties":{"title":{"type":"string"},"points":{"type":"number"}}}}' \
  --wait 5m --json

# Or fire and forget, then fetch the result later
npx webskillet start "Extract the title and points of the top Hacker News stories" --start-url https://news.ycombinator.com --json
npx webskillet result <run-id> --json

# Reuse the skillet from a previous run (its id is in the run output)
npx webskillet run "Extract the title and points of the top Hacker News stories" \
  --skillet-id <skillet-id> --parameters '{"count": 10}' --wait 5m --json
```

Other commands and flags (`list`, `--model <haiku|sonnet|opus>`, JSON files for `--parameters`/`--output-schema`): `npx webskillet --help`, or the docs: <https://webskillet.ai/docs/cli-reference>

## Python SDK

Use when building Webskillet into a Python codebase.

```bash
pip install webskillet
```

```python
from webskillet_client import WebskilletClient

client = WebskilletClient(api_key="YOUR_WEBSKILLET_API_KEY")  # user gets this from the Webskillet app

body = {
    "task": "Extract the title and points of the top Hacker News stories",
    "start_url": "https://news.ycombinator.com",
    "parameters": {"count": 5},
    "output_schema": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"title": {"type": "string"}, "points": {"type": "number"}},
        },
    },
}

# Start a run and wait for the result
run = client.runs.run(body=body, timeout_seconds=600)
print(run.result)

# Or fire and forget, then fetch the result later
started = client.runs.start(body=body)
current = client.runs.get(run_id=started.id)

# Reuse the skillet from a previous run
run = client.runs.run(
    body={**body, "skillet_id": run.skillet.id, "parameters": {"count": 10}},
    timeout_seconds=600,
)
```

Write the key as a placeholder or read it from an env var — the user supplies the real one.

Beyond the happy path: `runs.run()` raises `RunFailedError` when the run fails; `client.runs` also has `list` / `update`, `client.skillets.list()` shows saved skillets, and `AsyncWebskilletClient` mirrors it all with `await`. Details: <https://webskillet.ai/docs/sdks>

## TypeScript SDK

Use when building Webskillet into a TypeScript or JavaScript codebase.

```bash
npm install webskillet
```

```ts
import { WebskilletClient } from "webskillet/client-sdk";

const client = new WebskilletClient({ apiKey: process.env.WEBSKILLET_API_KEY! });

const body = {
  task: "Extract the title and points of the top Hacker News stories",
  startUrl: "https://news.ycombinator.com",
  parameters: { count: 5 },
  outputSchema: {
    type: "array",
    items: {
      type: "object",
      properties: { title: { type: "string" }, points: { type: "number" } },
    },
  },
};

// Start a run and wait for the result
const run = await client.runs.run(body, { timeoutMs: 600_000 });
if (run.status === "completed") console.log(run.result);

// Or fire and forget, then fetch the result later
const started = await client.runs.start(body);
const current = await client.runs.get(started.id);

// Reuse the skillet from a previous run
const rerun = await client.runs.run(
  { ...body, skilletId: run.skillet.id, parameters: { count: 10 } },
  { timeoutMs: 600_000 }
);
```

Beyond the happy path: `runs.run()` throws `WebskilletRunFailedError` when the run fails; `client.runs` also has `list` / `update`, and `client.skillets.list()` shows saved skillets. Details: <https://webskillet.ai/docs/sdks>

## HTTP API

Only when the user explicitly asks for the raw API.

The API key is in the Webskillet app at <https://webskillet.ai> — in the sidebar. Tell the user to set it as an environment variable in the terminal, and give them this command to run:

```bash
export WEBSKILLET_API_KEY="paste-your-key-here"
```

Then reference it from the environment in your requests — never paste the key itself into a command:

```bash
# Start a run
curl -X POST https://webskillet.ai/api/v1/runs/start \
  -H "x-api-key: $WEBSKILLET_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "task": "Extract the title and points of the top Hacker News stories",
    "startUrl": "https://news.ycombinator.com",
    "parameters": { "count": 5 },
    "outputSchema": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": { "title": { "type": "string" }, "points": { "type": "number" } }
      }
    }
  }'
# => { "id": "ru_...", "status": "pending" }

# Fetch the result — poll every ~5s until status is "completed" or "canceled"
curl https://webskillet.ai/api/v1/runs/ru_... -H "x-api-key: $WEBSKILLET_API_KEY"

# Reuse the skillet from a previous run: add "skilletId" to the start body
#   { "task": "...", "skilletId": "<skillet-id>", "parameters": { "count": 10 } }
```

Full reference: <https://webskillet.ai/docs/api-reference>

## Tips

- Put values that vary between runs in `parameters` instead of editing the task text.
- Set `outputSchema` when code consumes the result — the run validates against it.
- Always set a wait deadline (`--wait` / `timeout_seconds` / `timeoutMs`); waiting is unbounded by default.
