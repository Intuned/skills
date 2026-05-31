# Intuned target contract (ground truth)

Everything here was verified against real scaffolds (`intuned dev init`,
templates `python-starter`, `python-e-commerce-scrapingcourse`,
`python-browser-sdk-showcase`, `python-starter-auth`) and the Intuned docs.

## Project layout (one project per Crafted CLI, one API inside)

```
<task_id>/
├── api/
│   └── <name>.py                      # the single automation
├── utils/                             # optional: pydantic schemas, helpers
│   └── types_and_schemas.py
├── .parameters/
│   └── api/<name>/default.json        # default params -> must reproduce the task
├── Intuned.jsonc                      # manifest
├── pyproject.toml                     # py3.12, playwright==1.56, intuned-runtime, intuned-browser
└── intuned-resources/jobs/...         # generated; leave as-is
```

Auth projects additionally have:

```
├── auth-sessions/
│   ├── create.py                      # async def create(page, params)
│   └── check.py                       # async def check(page) -> bool
├── .parameters/auth-sessions/{create,check}/default.json
├── auth-sessions-instances/<id>/...   # local only, created by `dev run authsession create`
└── intuned-resources/auth-sessions/<id>.auth-session.jsonc
```

## The API contract

```python
from typing import TypedDict
from playwright.async_api import Page
# from intuned_runtime import extend_payload   # only if fan-out (not default)

class Params(TypedDict):
    # one field per surviving craft param, snake_case preserved
    ...

async def automation(page: Page, params: Params | None = None, **_kwargs):
    # page is INJECTED and already constructed. Never launch a browser.
    ...
    return result   # JSON-serializable dict/list -> becomes the run `output`
```

- Entry point name **must** be `automation`. File name (`api/<name>.py`) becomes
  the API name passed to `intuned dev run api <name>`.
- `params` arrives as a plain dict matching `.parameters/api/<name>/default.json`.
  Validate with a pydantic model if non-trivial.
- Return value is the run output. Do **not** print JSON as the result, do **not**
  write output files; `print()` is fine for log breadcrumbs (shows in run logs).

## intuned_browser SDK (navigation, files, helpers)

```python
from intuned_browser import go_to_url, save_file_to_s3, Attachment
# also: download_file, upload_file_to_s3, extract_markdown, sanitize_html,
#       resolve_url, click_until_exhausted, scroll_to_load_content,
#       process_date, validate_data_using_schema, filter_empty_values
from intuned_browser.ai import extract_structured_data, is_page_loaded
```

- `await go_to_url(page, url=..., timeout_s=15, retries=3, wait_for_load_using_ai=False)`
  — replaces `page.goto`; adds retries + reliable load wait.
- `await save_file_to_s3(page=page, trigger=<locator or url>)` → `Attachment`
  with `.file_name` and `await .get_signed_url()`. Only for true binary
  deliverables.

## intuned_runtime SDK

```python
from intuned_runtime import extend_payload, extend_timeout, persistent_store, attempt_store
from intuned_runtime import get_auth_session_parameters
from intuned_runtime.captcha import wait_for_captcha_solve
```

- `extend_payload({"api": "...", "parameters": {...}})` — Jobs fan-out. NOT used
  by default (ADR 0001).
- `await wait_for_captcha_solve(page=page, timeout_s=120.0)` — platform only.

## Intuned.jsonc manifest (key fields)

```jsonc
{
  "projectName": "<task_id>",
  "workspaceId": "<from auth whoami>",
  "apiAccess": { "enabled": true },          // enable so platform runs work
  "authSessions": { "enabled": false },      // true for auth ports, type "API"
  "replication": { "maxConcurrentRequests": 1, "size": "standard" },
  "headful": false,                          // true for protected sites
  "stealthMode": { "enabled": false },       // true for protected sites (PLATFORM ONLY)
  "captchaSolver": {                         // only if a captcha wall appears; needs headful+stealth
    "enabled": true,
    "cloudflare": { "enabled": true },
    "settings": { "autoSolve": true, "solveDelay": 2000, "maxRetries": 6, "timeout": 30000 }
  },
  "metadata": {
    "defaultRunPlaygroundInput": { "apiName": "<name>", "parameters": { ...task defaults... } }
  }
}
```

## CLI commands (verified, v0.1.8)

```bash
intuned auth whoami                                   # confirm login + workspaceId
intuned dev list-templates                            # template ids
intuned dev init <dir> --template python-starter \
    --language python --project-name <task_id> \
    --install-deps --non-interactive [--stealth]      # scaffold
# transform files in-place, then:
intuned dev run api <name> '<json-params>'            # LOCAL run (no stealth/captcha)
intuned dev run api <name> '<json>' --auth-session <id> --keep-browser-open --trace
intuned dev run authsession create '<json-creds>' --id <id>   # local auth session
intuned dev run authsession validate <id>
intuned dev deploy [--non-interactive]                # provision + deploy
intuned platform runs start '<json>' -p <task_id>     # DEPLOYED standalone run
intuned platform runs get <run-id>                    # poll result
```

`platform runs start` data shape: `{"api": "<name>", "parameters": {...}, "proxy": "http://..."}`
(proxy optional). The run is async — poll `runs get` until terminal.

## Hard constraints / gotchas (see gotchas.md for the living list)

- Python **3.12 only** (`requires-python = ">=3.12,<3.13"`). py3.10+ syntax fine.
- Playwright **1.56** is pinned by the template; stealth needs ≥1.55 (ok).
- `automation` is **async**; the craft's `asyncio.run(...)` wrapper must be removed.
- Stealth / captcha do **not** run locally — verify protected sites via deploy.
