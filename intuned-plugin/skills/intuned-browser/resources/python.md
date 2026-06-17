# intuned_browser (Python)

Reliable helpers for browser automation — handles retries, network failures, and dynamic content.

## Installation (if not already installed)

```bash
uv add intuned-browser
```

## Import

```python
from intuned_browser import go_to_url, wait_for_network_settled, extract_markdown
```

## Navigation

### go_to_url

Navigate with automatic retries on network failures.

```python
await go_to_url(page, url="https://example.com")
await go_to_url(page, url="https://example.com", wait_for_load_state="domcontentloaded")
```

### resolve_url

Convert relative URLs to absolute.

```python
absolute_url = await resolve_url(page=page, url="/products/123")
```

## Waiting

### wait_for_network_settled

Wait for network requests to complete.

```python
@wait_for_network_settled
async def click_element(page):
    await element.click()

await click_element()

```

### wait_for_dom_settled

Wait for DOM mutations to stop.

```python
await wait_for_dom_settled(source=page)
await wait_for_dom_settled(source=page, timeout_s=3000)
```

## Content Extraction

### extract_markdown

Convert HTML elements to markdown.

```python
markdown = await extract_markdown(header_locator)
```

## Pagination

### scroll_to_load_content

Scroll to trigger lazy-loaded content (infinite scroll).

```python
await scroll_to_load_content(page)
await scroll_to_load_content(page, max_scrolls=10)
```

### click_until_exhausted

Click a button repeatedly until disabled/hidden (load more pagination).

```python
await click_until_exhausted(page=page, button_locator=load_more_button, max_clicks=20)
```

## File Handling

**Note:** `save_file_to_s3` and `upload_file_to_s3` upload to Intuned's default managed S3 bucket (or your own, if you pass `S3Configs` / set `AWS_*` env vars).

### save_file_to_s3

Download a file and upload it to S3 in one step. Recommended for most attachment scenarios.

```python
# Trigger can be a URL string, a Playwright Locator, or a callback
attachment = await save_file_to_s3(page, trigger="https://example.com/report.pdf")
attachment = await save_file_to_s3(page, trigger=page.locator("a.download-btn"))
```

Returns an Attachment object with `key`, `suggested_file_name`, `bucket`, etc.

### download_file + upload_file_to_s3 (Custom Download Logic)

Use together when you need custom download/upload logic — processing the file before uploading, or using custom S3 configs.

**download_file** — Downloads a file via URL or Locator click:

```python
download = await download_file(page, "https://example.com/file.pdf")
download = await download_file(page, page.locator("button.download"))
```

**upload_file_to_s3** — Uploads a download or binary data to S3:

```python
download = await download_file(page, page.locator("a.pdf-link"))
attachment = await upload_file_to_s3(file=download)
```

Returns an Attachment object.

## Data Validation

### validate_data_using_schema

Validate extracted data against a JSON schema. Supports the custom `attachment` type.

```python
schema = {
    "type": "object",
    "required": ["name", "price"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "price": {"type": "number", "minimum": 0},
        "document": {"type": "attachment"},
    },
}

validate_data_using_schema(extracted_data, schema)
# Throws ValidationError if validation fails
```

## Common Patterns

### Navigate and Wait

```python
await go_to_url(page, url)

await wait_for_dom_settled(source=page)

@wait_for_network_settled(page=page)
async def click(page):
    await element.click()
await click(page)
```

### Handle Infinite Scroll

```python
await scroll_to_load_content(page, max_scrolls=20)
items = await page.query_selector_all(".item")
```

### Handle Load More Button

```python
await click_until_exhausted(page=page, button_locator=locator)
items = await page.query_selector_all(".item")
```

## Available Methods (Complete List)

**These are the ONLY methods available from `intuned_browser`. Do NOT import anything else from this package.**

| Method                       | Purpose                      |
| ---------------------------- | ---------------------------- |
| `go_to_url`                  | Navigate with retries        |
| `resolve_url`                | Resolve relative URLs        |
| `wait_for_network_settled`   | Wait for network idle        |
| `wait_for_dom_settled`       | Wait for DOM stable          |
| `extract_markdown`           | HTML to markdown             |
| `scroll_to_load_content`     | Infinite scroll              |
| `click_until_exhausted`      | Load more pagination         |
| `save_file_to_s3`            | Download + upload to S3      |
| `download_file`              | Download file only           |
| `upload_file_to_s3`          | Upload to S3 only            |
| `validate_data_using_schema` | Validate data against schema |
