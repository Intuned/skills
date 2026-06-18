# Intuned API File Patterns

Reference structures for an Intuned API file. Use these to shape a new API file or align an edit. These are structural patterns, **not stubs** and **not templates to stamp verbatim**: fill every function body with the real selectors, extraction, and navigation, and adapt the file to its actual role — function names, extraction method (DOM scraping vs network call), pagination type, chaining relationships, navigation flow. Do not leave `# TODO:` / `// TODO:` markers behind.

## Hard rules

- **Both Python and TypeScript** use hyphens for file/API names: `get-products.py`, `get-product-details.ts`.
- `extend_payload` / `extendPayload` `api` field must match the target API's filename without extension.
- **Always include** `validate_data_using_schema` / `validateDataUsingSchema` in the automation/handler function. Never skip it.
- **Never import external HTTP libraries** (`httpx`, `requests`, `axios`, etc.). Network calls use `page.evaluate()` with the browser's built-in `fetch()`.
- **Only import from** `intuned_browser`, `intuned_runtime`, `playwright`, and the standard library (Python) / `@intuned/browser`, `@intuned/runtime`, `playwright` (TypeScript). No third-party packages.
- **Never create or overwrite** auto-generated files: `pyproject.toml` (Python); `package.json`, `tsconfig.json` (TypeScript).
- The function names below (`navigate_to_page`, `extract_items`) are placeholders — name each function for what it does.

---

## Step 1 — Imports

Only import what the API actually uses.

**Python:**

```python
import logging
from playwright.async_api import Page
from intuned_browser import go_to_url, validate_data_using_schema
from intuned_runtime import extend_payload, extend_timeout

# Add if pagination is click-based / next-button:
from intuned_browser import wait_for_network_settled
# Add if pagination is infinite scroll:
from intuned_browser import scroll_to_load_content
# Add if pagination is load-more:
from intuned_browser import click_until_exhausted
# Add if the API downloads files as attachments:
from intuned_browser import save_file_to_s3
```

**TypeScript:**

```typescript
import { Page, BrowserContext } from "playwright";
import { goToUrl, validateDataUsingSchema } from "@intuned/browser";
import { extendPayload, extendTimeout } from "@intuned/runtime";

// Add if pagination is click-based / next-button:
import { withNetworkSettledWait } from "@intuned/browser";
// Add if pagination is infinite scroll:
import { scrollToLoadContent } from "@intuned/browser";
// Add if pagination is load-more:
import { clickUntilExhausted } from "@intuned/browser";
// Add if the API downloads files as attachments:
import { saveFileToS3 } from "@intuned/browser";
```

---

## Step 2 — DATA_SCHEMA (filled, not empty)

Set the top-level shape (**array** for list APIs, **object** for detail/simple APIs) and **fill in the real `properties` and `required`** for the fields the API extracts. See the main skill's "DATA_SCHEMA" and "Field type mapping" sections.

**List API (Python):**

```python
logger = logging.getLogger(__name__)

DATA_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "price": {"type": "number"},
            "detail_url": {"type": "string"},
        },
        "required": ["title", "detail_url"],
    },
}
```

**Detail / simple API (Python):**

```python
logger = logging.getLogger(__name__)

DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "documents": {"type": "array", "items": {"type": "attachment"}},
    },
    "required": ["title"],
}
```

TypeScript is identical in shape — `const DATA_SCHEMA: any = { ... }`.

---

## Step 3 — Navigation function (entry-point and simple APIs)

```python
async def navigate_to_listing(page: Page, parameters: dict) -> None:
    """Open the listing page."""
    await go_to_url(page, "https://example.com/listings")
    # real navigation: apply filters, dismiss banners, wait for content, etc.
```

```typescript
async function navigateToListing(page: Page, params: Record<string, any>): Promise<void> {
  await goToUrl({ page, url: "https://example.com/listings" });
  // real navigation: apply filters, dismiss banners, wait for content, etc.
}
```

---

## Step 4 — Action (extraction) function

DOM-scraping variant returns the extracted data. Implement the body with the page's selectors. Use `query_selector` / `query_selector_all` (Python) or `page.$()` / `page.$$()` (TypeScript) for reads.

```python
async def extract_items(page: Page) -> list[dict]:
    """Extract all solicitation rows on the current page."""
    rows = await page.query_selector_all(".view-solicitations .abstract")
    results: list[dict] = []
    for row in rows:
        title_el = await row.query_selector('h3[itemprop="name"]')
        title = (await title_el.inner_text()).strip() if title_el else ""
        # ...extract the rest of the fields with the page's selectors...
        results.append({"title": title})
    return results
```

### Step 4b — Action function, network-call variant

When this function extracts from a network endpoint, reproduce the request with `page.evaluate()` + the browser `fetch()` (never an external HTTP lib). The action function receives `parameters`.

```python
async def fetch_items(page: Page, parameters: dict) -> list[dict]:
    """Call the listing endpoint and map the response to the schema."""
    data = await page.evaluate(
        """async () => {
            const res = await fetch('/api/listings?page=1', { headers: { 'accept': 'application/json' } });
            return await res.json();
        }"""
    )
    return [{"title": it["name"], "detail_url": it["url"]} for it in data["items"]]
```

---

## Step 5 — Pagination functions (choose per plan)

**Click-based / next-button:**

```python
async def is_next_page_available(page: Page) -> bool:
    return await page.query_selector("a.pagination-next") is not None

@wait_for_network_settled(timeout_s=10)
async def go_to_next_page(page: Page) -> None:
    el = await page.query_selector("a.pagination-next")
    if el:
        await el.click()
```

> ⚠️ For **URL-based** pagination (`?page=N`), navigate with `go_to_url` and **build the absolute URL yourself** — `resolve_url` drops the path for query-only relatives (`resolve_url(page, "?page=1")` → site root). Compose from the current URL's path, or keep a base URL.

**Infinite scroll** — use `scroll_to_load_content` (Python) / `scrollToLoadContent` (TypeScript), passing the timeout heartbeat:

```python
async def load_more_content(page: Page, max_iterations: int = 5) -> None:
    await scroll_to_load_content(page, max_iterations=max_iterations, on_scroll_progress=extend_timeout)
```

**Load-more button** — use `click_until_exhausted` (Python) / `clickUntilExhausted` (TypeScript), passing `heartbeat=extend_timeout`.

---

## Step 6 — Automation / handler (compose per role + pagination)

The `automation` (Python) / default `handler` (TypeScript) is the entry point. Pick the matching shape; **include the `extend_payload` block only when this API chains to another**, and pass **all** plan-specified fields (not just the linking field).

### Entry point, click-based pagination (Python)

```python
async def automation(page: Page, parameters: dict) -> dict:
    await navigate_to_listing(page, parameters)
    all_items = []
    page_count = 0
    max_pages = parameters.get("max_pages", 5)
    while page_count < max_pages:
        extend_timeout()
        items = await extract_items(page)
        validate_data_using_schema(items, DATA_SCHEMA)
        all_items.extend(items)
        for item in items:
            if "detail_url" in item:
                extend_payload({"api": "get-details", "parameters": item})
        page_count += 1
        if not await is_next_page_available(page):
            break
        await go_to_next_page(page)
    return {"items": all_items, "total_pages": page_count}
```

### Entry point, infinite scroll / load-more (Python)

```python
async def automation(page: Page, parameters: dict) -> dict:
    await navigate_to_listing(page, parameters)
    extend_timeout()
    await load_more_content(page, max_iterations=parameters.get("max_scrolls", 5))
    items = await extract_items(page)
    validate_data_using_schema(items, DATA_SCHEMA)
    for item in items:
        if "detail_url" in item:
            extend_payload({"api": "get-details", "parameters": item})
    return {"items": items, "total_items": len(items)}
```

### Entry point, no pagination (Python)

```python
async def automation(page: Page, parameters: dict) -> dict:
    await navigate_to_listing(page, parameters)
    items = await extract_items(page)
    validate_data_using_schema(items, DATA_SCHEMA)
    return {"items": items, "total_items": len(items)}
```

### Entry point, network call (Python)

```python
async def automation(page: Page, parameters: dict) -> dict:
    await navigate_to_listing(page, parameters)  # establishes session/cookies
    extend_timeout()
    items = await fetch_items(page, parameters)
    validate_data_using_schema(items, DATA_SCHEMA)
    return {"items": items, "total_items": len(items)}
```

### Chained API — receives params from another API (Python)

```python
async def automation(page: Page, parameters: dict, **_kwargs) -> dict:
    detail_url = parameters.get("detail_url")
    if not detail_url:
        raise ValueError("detail_url parameter is required")
    await go_to_url(page, detail_url)
    data = await extract_detail(page)
    validate_data_using_schema(data, DATA_SCHEMA)
    return data
```

### TypeScript handler shape

Every TypeScript API exports a default `handler(params, page, context)` mirroring the Python `automation` above:

```typescript
export default async function handler(
  params: Record<string, any>,
  page: Page,
  context: BrowserContext
): Promise<Record<string, any>> {
  await navigateToListing(page, params);
  const items = await extractItems(page);
  validateDataUsingSchema({ data: items, schema: DATA_SCHEMA });
  for (const item of items) {
    if ("detailUrl" in item) extendPayload({ api: "get-details", parameters: item });
  }
  return { items, totalItems: items.length };
}
```

> `extend_payload` / `extendPayload` only fires in deployed Jobs, not local `dev attempt`. Local tests still validate everything else.

---

## Auth-session files (only if the API requires auth)

Auth-session APIs are a `create` (log in, save browser state) and a `check` (verify the saved state is still valid) pair. Files live in `auth-sessions/` at the project root (not in `api/`) — the **`auth-sessions`** skill covers their lifecycle in full. The code shapes are below.

**`auth-sessions/create.py`:**

```python
from typing import TypedDict
from playwright.async_api import Page
from intuned_browser import go_to_url


class Params(TypedDict):
    username: str
    password: str


async def create(page: Page, params: Params | None = None, **_kwargs):
    await go_to_url(page=page, url="https://example.com/login")
    # fill the login form from params, submit, wait for a logged-in-only element
```

**`auth-sessions/check.py`:**

```python
from playwright.async_api import Page
from intuned_browser import go_to_url


async def check(page: Page, **_kwargs) -> bool:
    await go_to_url(page=page, url="https://example.com/account")
    el = await page.query_selector(".user-menu")
    return el is not None
```

TypeScript: `export default async function create(params, page, context): Promise<void>` and `export default async function check(page, context): Promise<boolean>`, same logic.

---

## Build verification

After writing the file(s), confirm the project builds from the project root and fix any errors before reporting:

- **TypeScript**: `npx tsc --noEmit`
- **Python** (both must pass):
  - `uvx pyright --pythonpath "$(uv run which python)"`
  - `uv run python -m compileall . -x "\.venv" -q`

If an error involves an unknown `intuned_browser` / `@intuned/browser` / `intuned_runtime` / `@intuned/runtime` symbol, load the **`intuned-browser`** skill and check the correct signature.
