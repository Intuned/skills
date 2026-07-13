# intuned_files (Python)

## Installation (if not already installed)

```bash
uv add intuned-files
```

## File Object

Every operation takes a file dict with a `type` and **exactly one source** (`url`, `download`, `base64`, or `buffer`):

```python
{"type": "pdf", "url": "https://example.com/report.pdf"}
{"type": "pdf", "pages": [1, 2], "download": download_file(page, trigger)}  # download_file result, awaited or not
{"type": "spreadsheet", "sheetName": "Q1 Sales", "url": "https://example.com/data.xlsx"}  # sheetName required
{"type": "document", "url": "https://example.com/contract.docx"}
{"type": "image", "buffer": raw_bytes}
```

Prefer `download` for files coming from the site being automated (works with auth) and `url` for publicly fetchable files.

## Operations

### to_markdown

```python
from intuned_files import to_markdown

markdown = await to_markdown(
    {"type": "pdf", "url": "https://example.com/report.pdf"},
    label="convert_report",
)
```

### extract_tables

Returns a list of `ExtractedTable` with `page_number`, `title` (optional), and `content` (2D array of cell strings).

```python
from intuned_files import extract_tables

tables = await extract_tables(
    {"type": "pdf", "download": download_file(page, page.locator("a.download-report"))},
    label="report_tables",
)
```

### extract_structured_data

Converts the file to markdown, then runs AI extraction. `data_schema` accepts a JSON Schema dict or a Pydantic model class. Other optional kwargs: `prompt`, `model`, `max_retries`, `enable_cache`, `api_key`.

```python
from intuned_files import extract_structured_data

data = await extract_structured_data(
    {"type": "pdf", "download": download_file(page, page.locator("a.invoice-pdf"))},
    data_schema={
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "total": {"type": "number"},
        },
        "required": ["invoice_number", "total"],
    },
    label="parse_invoice",
)
```

## Processing Many Files in a Loop

Call `extend_timeout()` each iteration — file operations poll the backend and can take a while.

```python
from intuned_runtime import extend_timeout

for link in invoice_links:
    extend_timeout()
    data = await extract_structured_data(
        {"type": "pdf", "download": download_file(page, link)},
        data_schema=invoice_schema,
        label="parse_invoice",
    )
    results.append(data)
```

## Available Exports

`to_markdown`, `extract_tables`, and `extract_structured_data` are the ONLY functions available from `intuned_files` — do NOT import anything else. Typed models are also exported if preferred over dicts: `PdfFile`, `ImageFile`, `SpreadsheetFile`, `DocumentFile`, `ExtractedTable`.
