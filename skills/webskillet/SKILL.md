---
name: webskillet
description: Turn web tasks described in natural language into structured results, covering scraping, data extraction, multi-page form filling, and repetitive browser automation. This skill explains the three ways to consume it: the SDK, the CLI, and cURL against the HTTP API.
---

# Webtask

A webtask is a web automation described in natural language. Send an instruction like ("extract all listings from this directory") with an optional starting URL, parameters, and output schema. Webskillet's browser agent writes and runs whatever code the task needs and returns structured results. Runs are asynchronous: start one, poll until it completes, then read the result inline or from a download link. Every run belongs to a skillet, a saved automation that keeps the generated code and learned site knowledge, so passing the same `skilletId` makes repeat runs faster and cheaper.

## Install and consume

Webskillet is available on `https://webskillet.ai/`. It can also be consumed programmatically in three ways, all of which need an API key: sign in to `https://webskillet.ai/`, click **Get Code** on the task input, and copy the key from the drawer that opens.

### CLI

Install and authenticate:

```bash
npm install -g webskillet
webskillet auth login
```

Subcommands:

- `webskillet start <task>` — start a webtask and print its run ID immediately. Non-blocking.
- `webskillet run <task>` — start a webtask and poll every 5s until it finishes; `--wait <duration>` (`30s`, `10m`, `2h`) caps the wait, bare `--wait` means 10 minutes, omitted means wait indefinitely. Blocking.
- `webskillet result <web-task-id>` — get a webtask's status and result
- `webskillet list` — list recent webtasks (`-l, --limit`, default 20; `-o, --offset`)
- `webskillet auth login` / `webskillet auth logout` — manage stored credentials

`start` and `run` share the task flags: `--start-url <url>`, `--parameters <json-or-file>`, `--output-schema <json-or-file>`, `--skillet-id <id>` (reuse a saved skillet), and `--model <haiku|sonnet|opus>`. `--parameters` and `--output-schema` accept inline JSON or a path to a JSON file. `start`, `run`, `result`, and `list` accept `--json [filename]` for machine-readable output (printed, or written to the file when a filename is given).

Example:

```bash
webskillet run "Extract the title and URL of the top story" \
  --start-url https://news.ycombinator.com \
  --output-schema ./schema.json \
  --wait 5m --json
```

<!-- TODO: link to the CLI reference docs -->

### SDK

SDK Clients exist for TypeScript and Python. Both group run operations under `client.runs` — `start`, `get`, `list`, `update`, and `run` (start + poll every 5s until `completed` or `canceled`) — and default to `https://webskillet.ai` (override with the `baseUrl` / `base_url` option).

**TypeScript (`npm install webskillet`).**

```typescript
import { WebskilletClient } from "webskillet/client-sdk";

const client = new WebskilletClient({
  apiKey: process.env.WEBSKILLET_API_KEY!,
});

// Start and poll in one call; pass timeoutMs to cap the wait
const result = await client.runs.run({
  task: "Extract the title and URL of the top story",
  startUrl: "https://news.ycombinator.com",
  outputSchema: {
    type: "object",
    properties: { title: { type: "string" }, url: { type: "string" } },
  },
});
if (result.status === "completed") {
  console.log(result.result); // structured output matching outputSchema
}

// Or manage the lifecycle yourself
const { id } = await client.runs.start({
  task: "Extract the title",
});
const current = await client.runs.get(id);
const recent = await client.runs.list({ limit: 20 });
```

Constructor options go in a second argument — `new WebskilletClient({ apiKey }, { baseUrl })`. `run()` throws `WebskilletRunFailedError` when the run completes with outcome `failed`, and `WebskilletTimeoutError` when `timeoutMs` expires.

**Python (`pip install webskillet-client`)**
pass the key explicitly — there is no env-var fallback. `AsyncWebskilletClient` mirrors the same API:

```python
from webskillet_client import WebskilletClient

with WebskilletClient(api_key="your-webskillet-api-key") as client:
    result = client.runs.run(
        body={
            "task": "Extract the title and URL of the top story",
            "startUrl": "https://news.ycombinator.com",
            "outputSchema": {
                "type": "object",
                "properties": {"title": {"type": "string"}, "url": {"type": "string"}},
            },
        },
        timeout_seconds=600,  # omit to wait indefinitely
    )
    if result.status == "completed":
        print(result.result)  # structured output matching outputSchema
```

The other methods are `client.runs.start(body=...)`, `client.runs.get(run_id=...)`, and `client.runs.list(limit=..., offset=...)`. `run()` raises `RunFailedError` when the run completes with outcome `failed`.

<!-- TODO: link to the TypeScript and Python SDK docs -->

### cURL

The API lives at `https://webskillet.ai`; pass the key in the `x-api-key` header.

Start a webtask. Only `task` is required; optional fields are `startUrl`, `parameters` (free-form JSON object), `outputSchema` (JSON Schema), `skilletId` (reuse a saved skillet), `model` (`haiku` | `sonnet` | `opus`), `proxy`, and `auth`. Unknown fields are rejected:

```bash
curl -X POST https://webskillet.ai/api/v1/runs/start \
  -H "x-api-key: $WEBSKILLET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Extract the title and URL of the top story",
    "startUrl": "https://news.ycombinator.com",
    "outputSchema": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "url": { "type": "string" }
      }
    }
  }'
```

Returns `{ "id": "...", "status": "pending" }`. Poll until `status` is `completed` or `canceled` (in-flight runs report `pending`, then `started`). A completed run has `outcome` (`success` | `failed`) and `result` — the structured output matching your schema, or `{ "type": "file", "file": { "url", "contentType", "sizeBytes", "expiresAt" } }` with an expiring download URL for large outputs:

```bash
curl https://webskillet.ai/api/v1/runs/<id> \
  -H "x-api-key: $WEBSKILLET_API_KEY"
```

List recent webtasks:

```bash
curl "https://webskillet.ai/api/v1/runs?limit=20&offset=0" \
  -H "x-api-key: $WEBSKILLET_API_KEY"
```

<!-- TODO: link to the API reference docs -->
