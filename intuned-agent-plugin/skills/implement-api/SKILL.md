---
name: implement-api
user-invocable: false
description: "Write correct, robust Intuned API code: the right file shapes, a filled DATA_SCHEMA with validation, Intuned helpers over raw Playwright, timeout handling, and the common best-practice and validation pitfalls to avoid."
---

# Implement API

Writing an Intuned API is the capability of turning a plan and a set of selectors into one correct, robust API file: its Playwright code, its `DATA_SCHEMA`, the right helper calls, and proper timeout handling. This skill is about _how the code should look_ — the file shapes, the helpers to reach for, the schema and validation, and the mistakes that make an API flaky or wrong.

An Intuned API file lives at `api/<api-name>.{py|ts}`. A correct one always has a filled `DATA_SCHEMA`, real function bodies (no `# TODO:` / `// TODO:` stub markers), and a `validate_data_using_schema` / `validateDataUsingSchema` call.

## File shapes and patterns

`resources/api-patterns.md` holds the full structural reference: the API roles (entry-point / chained / simple), pagination types (click-based / infinite scroll / load-more / none), the DOM-scraping vs network-call extraction variants, the `automation` (Python) / default `handler` (TypeScript) signatures, the `extend_payload` chaining wiring, and the auth-session `create` / `check` shapes. Pick the pattern that matches the API's role, extraction method, pagination type, and chaining, and adapt it — these are structural patterns, not templates to stamp verbatim. Function names come from what each function actually does.

## DATA_SCHEMA

Write the full `DATA_SCHEMA` and the `validate_data_using_schema` / `validateDataUsingSchema` call. Choose the top-level shape — **array** for list APIs, **object** for detail/simple APIs — then fill `properties` (and `required`) with the fields the API extracts.

**List APIs** — `{"type": "array", "items": {"type": "object", "properties": {...}}}`:

**Python:**

```python
DATA_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "price": {"type": "number"},
        },
        "required": ["title", "price"]
    }
}
```

**TypeScript:**

```typescript
const DATA_SCHEMA: any = {
  type: "array",
  items: {
    type: "object",
    properties: {
      title: { type: "string" },
      price: { type: "number" },
    },
    required: ["title", "price"],
  },
};
```

**Detail APIs** — `{"type": "object", "properties": {...}}`:

**Python:**

```python
DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
    },
    "required": ["title", "description"]
}
```

**TypeScript:**

```typescript
const DATA_SCHEMA: any = {
  type: "object",
  properties: {
    title: { type: "string" },
    description: { type: "string" },
  },
  required: ["title", "description"],
};
```

### Field type mapping

Map each field's type to its JSON-schema shape:

| Field Type      | JSON Schema                                                           | Notes                 |
| --------------- | --------------------------------------------------------------------- | --------------------- |
| `string`        | `{"type": "string"}`                                                  | Text content          |
| `number`        | `{"type": "number"}`                                                  | Decimal numbers       |
| `integer`       | `{"type": "integer"}`                                                 | Whole numbers         |
| `boolean`       | `{"type": "boolean"}`                                                 | True/false            |
| `url`           | `{"type": "string"}`                                                  | URLs use string type  |
| `date`          | `{"type": "string"}`                                                  | Dates use string type |
| `attachment`    | `{"type": "attachment"}`                                              | Downloaded files      |
| `array<string>` | `{"type": "array", "items": {"type": "string"}}`                      | List of strings       |
| `array<object>` | `{"type": "array", "items": {"type": "object", "properties": {...}}}` | List of objects       |
| `object`        | `{"type": "object", "properties": {...}}`                             | Nested data           |

### Required vs optional

- Fields in the `required` array are mandatory; omitted fields are optional (can be null).
- For API chaining, always make the chained URL field required.

### Never remove validation

Always include `validate_data_using_schema` (Python) / `validateDataUsingSchema` (TypeScript) — it catches bugs early. When validation fails, fix `DATA_SCHEMA` to match your actual output (not the other way around) and fix extraction to match the schema's field names and types. **Never remove or comment out the validation call.**

First investigate _why_ it failed — schema mismatch, data edge case, or extraction bug — then fix the root cause. Common failures:

- **Optional vs required (most common)** — a field in `required` is sometimes missing from the data: either drop it from `required` or have extraction always supply a default. Conversely, a field that should always exist belongs in `required`.
- Schema field name ≠ extracted field → rename one to match.
- Schema says `"type": "number"` but the extracted value is a string → add parsing (e.g., `float(price_text.replace("$", ""))`).
- Top-level type mismatch → confirm the schema shape (array vs object) matches what the function returns.

## Intuned helpers

Prefer Intuned's helpers over raw Playwright in API code — they are more reliable and less flaky than custom implementations. The **`intuned-browser`** skill has the full helper reference; this is the quick reference for the ones you reach for most:

| Python Helper              | TypeScript Helper        | When to Use                                            |
| -------------------------- | ------------------------ | ------------------------------------------------------ |
| `go_to_url`                | `goToUrl`                | Navigate to any URL (auto-retries on network failures) |
| `resolve_url`              | `resolveUrl`             | Convert relative URLs to absolute                      |
| `wait_for_network_settled` | `withNetworkSettledWait` | After clicks/navigation that trigger API calls         |
| `wait_for_dom_settled`     | `withDomSettledWait`     | After actions that update the DOM dynamically          |
| `extract_markdown`         | `extractMarkdown`        | Convert HTML content to clean markdown                 |
| `scroll_to_load_content`   | `scrollToLoadContent`    | Pages with infinite scroll/lazy loading                |
| `click_until_exhausted`    | `clickUntilExhausted`    | "Load more" buttons that need repeated clicks          |
| `save_file_to_s3`          | `saveFileToS3`           | Upload downloaded files as attachments                 |

### Execution control

| Python Helper      | TypeScript Helper | When to Use                                                             |
| ------------------ | ----------------- | ----------------------------------------------------------------------- |
| `extend_timeout()` | `extendTimeout()` | Timeout-sensitive repeated or long-running work (resets 10-min timeout) |
| `extend_payload()` | `extendPayload()` | Chain APIs in Jobs - schedule work for another API to process           |

## Timeout handling

Every API execution has a **10-minute timeout**. Refreshing it is core to correct API code — repeated or long-running work that doesn't refresh will be killed mid-run, and a fast local machine is not evidence that coverage is safe. Use `extend_timeout()` from `intuned_runtime` (Python) / `extendTimeout()` from `@intuned/runtime` (TypeScript):

1. In every `for`, `async for`, or `while` loop that does browser work, extraction, pagination, downloads, or awaits, refresh timeout as the first executable statement in the loop body, before the first `await`.
2. Before one-off long operations (large navigation, downloads, CAPTCHA), refresh timeout immediately before the operation.
3. Infinite scroll helpers: pass `on_scroll_progress=extend_timeout` (Python) / `onScrollProgress: extendTimeout` (TypeScript).
4. Load-more helpers: pass `heartbeat=extend_timeout` (Python) / `heartbeat: extendTimeout` (TypeScript).
5. Preserve existing timeout refreshes; add missing ones when loops/helpers require them.
6. Import `extend_timeout` / `extendTimeout` wherever timeout refresh is used.

### extend_payload()

`extend_payload` / `extendPayload` schedules another API to run, for chaining APIs in deployed Jobs (it only fires in Jobs, not in local runs). The `"api"` field must match the target filename without extension.

**Python:**

```python
from intuned_runtime import extend_payload

for item in items:
    if "target_url" in item:
        extend_payload({
            "api": "target-api-name",  # Matches filename without extension
            "parameters": {"url": item["target_url"]}
        })
```

**TypeScript:**

```typescript
import { extendPayload } from "@intuned/runtime";

for (const item of items) {
  if ("targetUrl" in item) {
    extendPayload({
      api: "target-api-name", // Matches filename without extension
      parameters: { url: item.targetUrl },
    });
  }
}
```

## Playwright best practices

- **Never use `element_id` values in the code.** Element IDs are temporary IDs injected dynamically by the browser tools (to make them work); they do **not** exist in the real DOM. Every selector you write must come from `build-selectors` (`build_reliable_selector` / `build_field_selector`), never an `element_id`.
- Add `xpath=` prefix to XPath selectors.
- For **data extraction** (scraping text, attributes, lists), use `query_selector` / `query_selector_all` (Python) or `page.$()` / `page.$$()` (TypeScript) instead of `.locator()` — they return elements directly and are faster for read operations. `.locator()` is fine for **interactions** (clicking, filling, selecting).
- Check an element exists before interacting: `if element: await element.click()` (Python) / `if (element) await element.click()` (TypeScript).
- Use intuned_browser helpers for waiting: `wait_for_network_settled` / `wait_for_dom_settled` / `go_to_url` (Python) or `withNetworkSettledWait` / `withDomSettledWait` / `goToUrl` (TypeScript).
- Call `extend_timeout()` (Python) / `extendTimeout()` (TypeScript) as the first executable statement in timeout-sensitive loops.

**Waiting example (Python):**

```python
from intuned_browser import wait_for_network_settled

@wait_for_network_settled(timeout_s=10)
async def click_button(page):
    button = await page.query_selector("button[data-test='submit']")
    if button:
        await button.click()

await click_button(page=page)
```

**Waiting example (TypeScript):**

```typescript
import { withNetworkSettledWait } from "@intuned/browser";

await withNetworkSettledWait(
  async (page) => {
    const button = await page.$("button[data-test='submit']");
    if (button) await button.click();
  },
  { page, timeoutInMs: 10000 },
);
```

**Avoid:**

- `page.close()` — the page is managed by the Intuned runtime; only close pages you explicitly created yourself.
- `page.wait_for_load_state()` — unreliable across sites; use the network/DOM settled helpers instead.
- `time.sleep()` (Python) / synchronous `sleep()` (TypeScript) / `page.wait_for_timeout()` — hard-coded waits cause flaky tests on slower environments; wait for actual readiness with `wait_for_dom_settled` / `wait_for_network_settled`.
- External HTTP libraries (`httpx`, `requests`, `axios`, etc.) — reproduce network calls with `page.evaluate()` and the browser's built-in `fetch()`.

### Resolve-url gotcha

For **URL-based** pagination (`?page=N`), build the absolute URL yourself and navigate with `go_to_url` / `goToUrl`. `resolve_url` / `resolveUrl` drops the path for query-only relative URLs — `resolve_url(page, "?page=1")` resolves to the **site root**, not the current page. Compose the absolute URL from the current URL's path (or keep a base URL), don't feed a bare query string to the resolver.

## Attachments

**Downloadable files are first-class data — capture them as Intuned attachments, not bare URLs.** For an `attachment`-type field (a PDF, .docx, .xlsx, .csv, .zip, an "export"/"download" link, etc.), download and upload the file with `save_file_to_s3` (Python, from `intuned_browser`) / `saveFileToS3` (TypeScript, from `@intuned/browser`) and return the resulting `Attachment` object as-is for that field. The **`handle-attachments`** skill covers the `Attachment` object shape, the triggers, and the per-page-type rules. Skip downloads that require login, error out, or redirect to a login/CAPTCHA page.

## Network calls

When an API extracts data from a network endpoint instead of the DOM, reproduce the request with `page.evaluate()` + the browser's `fetch()` (never an external HTTP lib) and map the response to the schema — see the network-call variant in `resources/api-patterns.md`. The **`find-network-requests`** skill covers discovering and capturing the right request.

## Default input file

- **Entry-point APIs** (no forwarded payload) — the parameters a run would start with, e.g. `{"max_pages": 2}`, or `{}` if the API takes none. Note that some apis may have large data quantities or may have many pages, so use small values in the .parameters/ so that you can attempt APIs faster instead of running an API across everything.
- **Chained / detail APIs** (receive a forwarded payload) — a representative example of that payload (e.g. one real `detail_url` plus the other forwarded fields) so the API is runnable on its own.

Create it with `mkdir -p .parameters/api/<api-name>` then write the file. Don't leave `.parameters` empty — a project with APIs but no default inputs can't be run from the playground.

## Testing locally

Run the API with `export MODE=generate_code && intuned dev attempt api <name> <params>` (see `intuned-cli`'s `dev_attempt.md`). generate_code MODE is local testing mode, which mocks file/attachment uploads (no real S3 or provisioned project needed). For an attachment API, you'll get mock `Attachment` objects back; a non-empty list means the upload path works. Real uploads happen later on `dev test-job` / deployed runs.

## Build verification

Confirm the code compiles cleanly from the project root and fix errors before reporting:

- **TypeScript**: `npx tsc --noEmit`
- **Python** (run both; fix failures before proceeding):
  1. **Static types (Pyright)**: `uvx pyright --pythonpath "$(uv run which python)"`
  2. **Syntax / import graph (bytecode compile)**: `uv run python -m compileall . -x "\.venv" -q`

If the error involves an unknown function or method from `intuned_browser` / `@intuned/browser` or `intuned_runtime` / `@intuned/runtime`, load the **`intuned-browser`** skill and validate the signature.
