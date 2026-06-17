# @intuned/browser (TypeScript)

Reliable helpers for browser automation — handles retries, network failures, and dynamic content.

## Installation (if not already installed)

```bash
yarn add @intuned/browser
```

## Import

```typescript
import {
  goToUrl,
  withNetworkSettledWait,
  waitForDomSettled,
  extractMarkdown,
  scrollToLoadContent,
  clickUntilExhausted,
  saveFileToS3,
  downloadFile,
  uploadFileToS3,
  resolveUrl,
  validateDataUsingSchema,
} from "@intuned/browser";
```

## Navigation

### goToUrl

Navigate with automatic retries on network failures.

```typescript
await goToUrl({ page, url: "https://example.com" });
await goToUrl({
  page,
  url: "https://example.com",
  waitForLoadState: "domcontentloaded",
});
```

### resolveUrl

Convert relative URLs to absolute.

```typescript
const absoluteUrl = await resolveUrl({
  url: "/lists/table",
  page: page,
});
```

## Waiting

### withNetworkSettledWait

Execute a callback and wait for network activity to settle.

```typescript
await withNetworkSettledWait(
  async (page) => {
    await page.click("button");
  },
  {
    page,
    timeoutInMs: 15000,
    maxInflightRequests: 0,
  }
);
```

### waitForDomSettled

Wait for DOM mutations to stop.

```typescript
const settled = await waitForDomSettled({
  source: page,
  settleDurationMs: 1000,
  timeoutInMs: 20000,
});
```

## Content Extraction

### extractMarkdown

Convert HTML elements to markdown.

```typescript
const markdown = await extractMarkdown({ source: headerLocator });
```

## Pagination

### scrollToLoadContent

Scroll to trigger lazy-loaded content (infinite scroll).

```typescript
await scrollToLoadContent({
  source: page,
});
```

### clickUntilExhausted

Click a button repeatedly until disabled/hidden (load more pagination).

```typescript
await clickUntilExhausted({
  page,
  buttonLocator: loadMoreButton,
  maxClicks: 20,
});
```

## File Handling

**Note:** `saveFileToS3` and `uploadFileToS3` upload to Intuned's default managed S3 bucket (or your own, if you pass `configs` / set `AWS_*` env vars).

### saveFileToS3

Download a file and upload it to S3 in one step. Recommended for most attachment scenarios.

```typescript
const attachment = await saveFileToS3({
  page,
  trigger: "https://example.com/report.pdf",
});
const attachment = await saveFileToS3({
  page,
  trigger: page.locator("a.download-btn"),
});
```

Returns an Attachment object with `key`, `suggestedFileName`, `bucket`, etc.

### downloadFile + uploadFileToS3 (Custom Download Logic)

Use together when you need custom download/upload logic — processing the file before uploading, or using custom S3 configs.

**downloadFile** — Downloads a file via URL, Locator click, or callback:

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

**uploadFileToS3** — Uploads a Playwright Download object (or binary data) to S3:

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

S3 config fallback: explicit configs → environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_BUCKET`) → Intuned's managed S3 storage.

Returns an Attachment object.

## Data Validation

### validateDataUsingSchema

Validate extracted data against a JSON schema. Supports the custom `attachment` type.

```typescript
const schema = {
  type: "object",
  required: ["name", "price"],
  properties: {
    name: { type: "string", minLength: 1 },
    price: { type: "number", minimum: 0 },
    document: { type: "attachment" },
  },
};

validateDataUsingSchema({ data: extractedData, schema });
// Throws ValidationError if validation fails, returns nothing if it passes
```

## Common Patterns

### Navigate and Wait

```typescript
await goToUrl({ page, url });
await withNetworkSettledWait(async () => {}, { page });
await waitForDomSettled({ source: page });
```

### Handle Infinite Scroll

```typescript
await scrollToLoadContent({ source: page });
const items = await page.locator(".item").all();
```

### Handle Load More Button

```typescript
await clickUntilExhausted({ page, buttonLocator: loadMoreButton });
const items = await page.locator(".item").all();
```

## Available Methods (Complete List)

**These are the ONLY methods available from `@intuned/browser`. Do NOT import anything else from this package.**

| Method                    | Purpose                      |
| ------------------------- | ---------------------------- |
| `goToUrl`                 | Navigate with retries        |
| `resolveUrl`              | Resolve relative URLs        |
| `withNetworkSettledWait`  | Wait for network idle        |
| `waitForDomSettled`       | Wait for DOM stable          |
| `extractMarkdown`         | HTML to markdown             |
| `scrollToLoadContent`     | Infinite scroll              |
| `clickUntilExhausted`     | Load more pagination         |
| `saveFileToS3`            | Download + upload to S3      |
| `downloadFile`            | Download file only           |
| `uploadFileToS3`          | Upload to S3 only            |
| `validateDataUsingSchema` | Validate data against schema |
