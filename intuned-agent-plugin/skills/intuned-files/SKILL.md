---
name: intuned-files
user-invocable: false
description: "Read and process file contents with the Intuned files SDK (intuned-files for Python / @intuned/files for TypeScript). ALWAYS read this skill when the user mentions reading files or processing their data — parsing, converting, or extracting data from PDFs, Word documents (.docx), Excel spreadsheets (.xlsx), or images — when the data to extract lives inside a file or image on the page rather than in the page's DOM, or when planning or writing automation code that must read file contents at runtime (generated code has no vision; this SDK is how it reads files). Covers converting files to markdown, extracting tables, extracting schema-shaped structured data (e.g. invoice fields from a PDF), file sources (URL, download, base64, buffer), cost/caching behavior, and when file processing is justified vs. extracting from the page."
---

# Intuned Files SDK

Read and process file **contents**: convert to markdown (`extract_markdown_from_file` / `extractMarkdownFromFile`), extract tables (`extract_tables_from_file` / `extractTablesFromFile`), and extract schema-shaped structured data (`extract_structured_data_from_file` / `extractStructuredDataFromFile`). Supported types: **PDF**, **image** (PNG/JPEG), **spreadsheet** (`.xlsx` only), and **document** (`.docx` only).

This is different from attachments (`save_file_to_s3` / `saveFileToS3`), which store files without reading them. Use this SDK when the automation needs the **data inside** a file.

## When to Use File Operations

**Prefer the website over files.** File operations are metered per page processed, and structured extraction additionally spends AI credits. If the requested data is visible on the site itself, extract it from the page with normal selectors — that is faster, cheaper, and more reliable.

Reach for file operations only when:

- The requested data exists **only inside files** and is not rendered on any page, **or**
- The user **explicitly requests file processing** (e.g. "parse the downloaded invoices", "read the PDF report").

**When file processing is needed, this SDK is the way to do it.** Do not use third-party parsing libraries (`pdfplumber`, `openpyxl`, `pdftotext`, OCR libs, etc.) unless you have confirmed the Intuned files SDK cannot handle that file type or operation.

## Cost and Caching

- Every **non-cached page processed is billed** to the workspace, and structured extraction spends AI credits on top.
- **Results are cached by file content** (checksum, per workspace). Re-processing an identical file is billed as **zero pages**, regardless of source — so repeated test runs and retries on the same file are cheap; do not build your own caching around these helpers. If the file's bytes change, it is processed (and billed) again.
- For PDFs and documents, pass `pages` when you only need specific pages — unneeded pages are wasted cost.
- Pass the optional `label` so usage is attributable in billing/monitoring (e.g. `label="parse_invoice"`).

## Requirements

- **Provisioned platform project required.** These helpers call Intuned backend functions, so the project must exist on the Intuned platform (`Intuned.json` must have a `projectName`). If it isn't provisioned yet, run `intuned dev provision --non-interactive` (see the `create-intuned-project` skill's project-setup phase). They only run inside the Intuned runtime — not as standalone scripts.
- **Structured extraction requires the browser SDK** (`intuned-browser` / `@intuned/browser`) to be installed; the other two operations do not.

## Language References

Read the resource for the project's language — it has signatures, examples, and patterns:

- **Python** (`intuned-files`): `resources/python.md`
- **TypeScript** (`@intuned/files`): `resources/typescript.md`

## Full Documentation

**When you need additional details — arguments, return types, extra examples, or if you encounter an error with any of these methods — consult the official documentation.**

**Do NOT read from `venv/`, `node_modules/`, or source files to discover function signatures. The docs are the source of truth.**

1. `search_intuned` — find the page for the helper you need (e.g. `extractMarkdownFromFile`, `extract_tables_from_file`).
2. `query_docs_filesystem_intuned` — read that page for full arguments, return types, and examples.
