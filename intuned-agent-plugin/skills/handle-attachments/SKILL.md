---
name: handle-attachments
user-invocable: false
description: "Capture downloadable files (PDFs, .docx/.xlsx/.csv/.zip, export/download links) as Intuned attachments — download them, upload to S3, and return the Attachment object for an attachment-type schema field. Load whenever a page exposes downloadable files you need to capture."
---

# Handle Attachments

Handling attachments is the capability of turning a page's downloadable files into Intuned `Attachment` objects. You identify what triggers a download, download the file, upload it to S3 with the file-handling helpers, and return the resulting `Attachment` as-is for any `attachment`-type field in your output schema.

The flow is always the same:

```
Identify trigger → Download file → Upload to S3 → Return Attachment object
```

1. **Identify** — find the element or URL that triggers the download.
2. **Download** — capture the file via Playwright.
3. **Upload** — store it in Intuned's S3 bucket.
4. **Return** — include the `Attachment` object in your results.

## The `attachment` type

`attachment` is a custom Intuned schema field type for downloadable files. It is distinct from a plain `url`: a `url` field holds a link string, while an `attachment` field holds a downloaded file that has been uploaded to S3 and is represented by an `Attachment` object.

**Downloadable files are `attachment` fields, not URLs.** When a page exposes a downloadable file (PDF, `.docx`/`.xlsx`/`.csv`/`.zip`, an "export"/"download" link or button), capture it as an attachment rather than downgrading it to a plain `url`.

In a schema, an attachment field is declared with `{"type": "attachment"}` (Python) / `{ type: "attachment" }` (TypeScript), and `validate_data_using_schema` / `validateDataUsingSchema` accept the custom `attachment` type.

## What counts as an attachment

Attachments are files that:

- Can be downloaded from the page.
- Are associated with a specific item (not global site resources).

Examples:

- Main documents for an entity.
- Supplementary/addendum documents.
- Summary documents.
- Forms, templates, registration documents.

### How to identify them on a page

- **By file extension** — links to common file types:
  - `.pdf`, `.doc`, `.docx`
  - `.xls`, `.xlsx`, `.csv`
  - `.ppt`, `.pptx`
  - `.zip`, `.rar`
- **By text** — download-related labels: "Download", "Export", "Save", "Get", "View".
- **By JavaScript** — dynamic download mechanisms:
  - `onclick` handlers
  - `data-download-url` attributes
  - JavaScript URLs

### Download triggers

A file can be downloaded via:

| Trigger type  | Description                            |
| ------------- | -------------------------------------- |
| URL link      | Direct link to file (`href` attribute) |
| Click element | Button/link that initiates download    |
| JavaScript    | Dynamic download triggered by script   |

## Download + upload to S3

**Note:** files upload to Intuned's default managed S3 bucket (or your own, if you pass `S3Configs` / set `AWS_*` env vars).

> **Local testing vs. real upload.** When testing locally with `export MODE=generate_code` (the standard `dev attempt` testing mode), uploads are **mocked** — `save_file_to_s3` returns a placeholder `Attachment` with no real upload, so no provisioning is needed. Real uploads (deployed runs and `dev test-job`) go to managed S3 and require the project to be **provisioned**, or they fail with a `401`.

### `save_file_to_s3` / `saveFileToS3` — download + upload in one step

Recommended for most attachment scenarios. The trigger can be a URL string, a Playwright `Locator`, or a callback.

```python
from intuned_browser import save_file_to_s3

# Trigger can be a URL string, a Playwright Locator, or a callback
attachment = await save_file_to_s3(page, trigger="https://example.com/report.pdf")
attachment = await save_file_to_s3(page, trigger=page.locator("a.download-btn"))
```

```typescript
import { saveFileToS3 } from "@intuned/browser";

const attachment = await saveFileToS3({
  page,
  trigger: "https://example.com/report.pdf",
});
const attachment = await saveFileToS3({
  page,
  trigger: page.locator("a.download-btn"),
});
```

Returns an `Attachment` object with `key`, `suggested_file_name` / `suggestedFileName`, `bucket`, etc.

### `download_file` + `upload_file_to_s3` / `downloadFile` + `uploadFileToS3` — custom download logic

Use these together when you need custom download/upload logic — processing the file before uploading, or using custom S3 configs.

**Download** — downloads a file via URL or `Locator` click:

```python
download = await download_file(page, "https://example.com/file.pdf")
download = await download_file(page, page.locator("button.download"))
```

```typescript
// URL trigger — opens URL in a new page, captures download, closes page
const download = await downloadFile({
  page,
  trigger: "https://example.com/file.pdf",
});

// Locator trigger — clicks element, captures download
const download = await downloadFile({
  page,
  trigger: page.locator("button.download"),
});

// Callback trigger — execute custom logic, capture first triggered download
const download = await downloadFile({
  page,
  trigger: async (page) => {
    await page.locator("button.export").click();
  },
});
```

**Upload** — uploads a download (or binary data) to S3:

```python
download = await download_file(page, page.locator("a.pdf-link"))
attachment = await upload_file_to_s3(file=download)
```

```typescript
const download = await downloadFile({
  page,
  trigger: page.locator("a.pdf-link"),
});
const attachment = await uploadFileToS3({ file: download });

// With custom S3 config
const attachment = await uploadFileToS3({
  file: download,
  configs: {
    bucket: process.env.AWS_BUCKET,
    region: process.env.AWS_REGION,
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
  fileNameOverride: "reports/monthly-report.pdf",
});
```

S3 config fallback (TypeScript): explicit configs → environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET`) → Intuned's managed S3 storage.

Both helpers return an `Attachment` object.

### Returning the attachment

Return the `Attachment` object **as-is** for any `attachment`-type field in your output schema — do not convert it to a string or URL:

```python
# Return directly for attachment-type fields in your schema
attachment = await save_file_to_s3(page, trigger="https://example.com/report.pdf")
```

```typescript
// Return directly for attachment-type fields in your schema
const attachment = await saveFileToS3({ page, trigger: "https://example.com/report.pdf" });
```

## The Attachment object

`save_file_to_s3` / `saveFileToS3` and `upload_file_to_s3` / `uploadFileToS3` return an `Attachment` — a custom Intuned type representing an uploaded file in S3.

### Properties

| Python                | TypeScript          | Description                                         |
| --------------------- | ------------------- | -------------------------------------------------- |
| `file_name`           | `fileName`          | Name/key of the file in the S3 bucket              |
| `key`                 | `key`               | S3 object key                                      |
| `bucket`              | `bucket`            | S3 bucket name                                     |
| `region`              | `region`            | AWS region                                         |
| `endpoint`            | `endpoint`          | Optional custom S3 endpoint (default: standard AWS) |
| `suggested_file_name` | `suggestedFileName` | Human-readable filename for display                |
| `file_type`           | `fileType`          | File type (`AttachmentType`)                        |

### Methods

| Python                                          | TypeScript                                   | Description                              |
| ----------------------------------------------- | -------------------------------------------- | ---------------------------------------- |
| `await attachment.get_signed_url(expiration=)`  | `await attachment.getSignedUrl(expiration?)` | Presigned download URL (default: 5 days) |
| `attachment.get_s3_key()`                       | `attachment.getS3Key()`                      | Full S3 URL                              |
| `attachment.to_dict()`                          | `attachment.toDict()`                        | Dictionary/record representation         |

### Getting a download URL

To produce a shareable download link for an uploaded attachment, call `get_signed_url` / `getSignedUrl` — it returns a presigned URL (default expiration: 5 days). Use `get_s3_key` / `getS3Key` for the full S3 URL.

## Attachments by page type

- **Listing page** — only consider attachments visible directly in the list.
- **Details page** — attachments can be found within the item's detail page.

## Downloads to skip

Skip downloads that:

- Require login/authentication.
- Show authorization errors.
- Redirect to login pages.
- Require captchas.
