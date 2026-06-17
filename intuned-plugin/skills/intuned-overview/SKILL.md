---
name: intuned-overview
description: "What Intuned is and its core concepts — projects, the project layout, what an API is and how its file is structured, jobs, and attachments. Load for orientation when you're new to how an Intuned project and the platform fit together."
---

# What is Intuned?

Intuned is a browser automation platform that turns web interactions into callable APIs. Instead of manually clicking through websites, developers write code that automates browsers using Playwright, then deploy that code to run reliably at scale.

Think of it as writing functions that control web browsers. These functions can extract data, fill forms, navigate pages, and handle complex workflows — all programmatically.

## Why Intuned?

- **Code-based automation** — Write real code (Python or TypeScript), not low-code workflows
- **Playwright-powered** — Full browser control with a battle-tested automation library
- **Cloud execution** — Run automations on Intuned's infrastructure without managing browsers
- **Local development** — Test and debug locally before deploying

---

## Core Concepts

### Projects

An Intuned **project** is a container for related browser automation code. Everything for a specific automation goal lives in one project.

**Python project:**

```text
project/
├── api/                                  # Your automation scripts
│   └── get-products.py                   # Each file = one API
├── .parameters/api/<name>/default.json   # Test inputs for each API
├── Intuned.json                          # Project configuration
├── pyproject.toml                        # Dependencies
└── README.md                             # What this project does
```

**TypeScript project:**

```text
project/
├── api/                                  # Your automation scripts
│   └── get-products.ts                   # Each file = one API
├── .parameters/api/<name>/default.json   # Test inputs for each API
├── Intuned.json                          # Project configuration
├── package.json                          # Dependencies
└── README.md                             # What this project does
```

### APIs

**What is an API?**

In Intuned, an API is a function that executes browser automation to perform an action or extract specific data from the web. Each API is a single file in the `api/` folder. All Intuned APIs rely on Playwright to perform the automation.

**How APIs Work**

```text
Parameters → Browser Opens → Automation Runs → Data Returned
```

1. API receives input parameters (URLs, search terms, IDs, etc.)
2. A Playwright browser instance is provided to your function
3. Your automation code runs (navigate, click, extract)
4. Structured data (JSON) is returned

**API Structure**

Python:

```python
from typing import TypedDict
from playwright.async_api import Page


class Params(TypedDict):
    required_field: str           # Always required
    optional_field: str | None    # Optional, defaults to None


async def automation(page: Page, params: Params | None = None, **_kwargs):
    if not params:
        params = {}

    result = {}
    # Your automation code here
    return result
```

TypeScript:

```typescript
import { Page, BrowserContext } from "playwright";

interface Params {
  url: string;
  limit?: number;
}

export default async function handler(
  params: Params,
  page: Page,
  context: BrowserContext
): Promise<Record<string, any>> {
  const result: Record<string, any> = {};
  // Your automation code here
  return result;
}
```

**Components**

1. **Params** — defines input parameters. Use `TypedDict` (Python) or `interface` (TypeScript). Optional fields use `| None` (Python) or `?` (TypeScript).

2. **Handler function** — the main entry point.

   - Python: called `automation`, receives `page`, `params`, `**_kwargs`
   - TypeScript: default export, typically called `handler`, receives `params`, `page`, `context`

3. **Return value** — always return an object with structured data.

**File naming**

- File name becomes the API name. Python: `api/get-products.py` → API name is `get-products`; TypeScript: `api/get-products.ts` → `get-products`.
- A typical project has several: a list API, a detail API, an action API, etc.

For how to actually write a correct, well-structured API file, see the **`implement-api`** skill.

**Multiple APIs Working Together**

APIs can be chained together using `extend_payload` (Python) / `extendPayload` (TypeScript) — one API schedules another with a payload. The `create-intuned-project` and `edit-intuned-project` flows cover the chaining patterns.

### Jobs (Batched Execution)

**What are Jobs?**

Jobs enable parallel execution of multiple API calls with retry logic and concurrency control. They're the primary way to run deployed APIs at scale.

**When to Use Jobs**

- Running the same API with different parameters
- Processing multiple items in parallel
- Need retry logic for reliability
- Want to control concurrency
- List API discovers items → schedules Detail API for each
- Any workflow where one API needs to trigger others

**Dynamic Payloads with extend_payload/extendPayload**

```text
Job starts → List API runs → extend_payload called → Detail APIs added to Job
```

When you call `extend_payload`, new API calls are added to the current Job's queue.

**Important:** `extend_payload` only works when running within a Job context (batched execution). It does nothing when running locally.

For the `.job.json` schema and how to create/manage jobs, see the **`manage-jobs`** skill.

### Attachments

Attachments are downloadable files (PDFs, documents, images) associated with items on a web page. Intuned captures these and uploads them to S3 storage.

```text
Identify Trigger → Download File → Upload to S3 → Return Attachment Object
```

File handling functions return an `Attachment` object — a custom Intuned type representing an uploaded file in S3, with metadata like bucket, key, filename, and methods to generate presigned download URLs.

For triggers, identification patterns, the `Attachment` type, and implementation details, see the **`handle-attachments`** skill.

---

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
