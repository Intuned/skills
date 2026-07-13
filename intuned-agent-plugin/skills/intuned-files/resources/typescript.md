# @intuned/files (TypeScript)

## Installation (if not already installed)

```bash
yarn add @intuned/files
```

## File Object

Every operation takes a file object with a `type` and **exactly one source** (`url`, `download`, `base64`, or `buffer`):

```typescript
{ type: "pdf", url: "https://example.com/report.pdf" }
{ type: "pdf", pages: [1, 2], download: downloadFile({ page, trigger }) } // downloadFile result, awaited or not
{ type: "spreadsheet", sheetName: "Q1 Sales", url: "https://example.com/data.xlsx" } // sheetName required
{ type: "document", url: "https://example.com/contract.docx" }
{ type: "image", buffer: rawBuffer }
```

Prefer `download` for files coming from the site being automated (works with auth) and `url` for publicly fetchable files.

## Operations

### toMarkdown

```typescript
import { toMarkdown } from "@intuned/files";

const markdown = await toMarkdown(
  { type: "pdf", url: "https://example.com/report.pdf" },
  { label: "convert_report" }
);
```

### extractTables

Returns `ExtractedTable[]` with `pageNumber`, `title` (nullable), and `content` (2D array of cell strings).

```typescript
import { extractTables } from "@intuned/files";

const tables = await extractTables(
  {
    type: "pdf",
    download: downloadFile({ page, trigger: page.locator("a.download-report") }),
  },
  { label: "report_tables" }
);
```

### extractStructuredData

Converts the file to markdown, then runs AI extraction. `dataSchema` is required and accepts a JSON Schema object or a zod schema. Other options: `prompt`, `model`, `maxRetries`, `enableCache`, `apiKey`.

```typescript
import { extractStructuredData } from "@intuned/files";
import { z } from "zod";

const data = await extractStructuredData(
  {
    type: "pdf",
    download: downloadFile({ page, trigger: page.locator("a.invoice-pdf") }),
  },
  {
    dataSchema: z.object({
      invoiceNumber: z.string(),
      total: z.number(),
    }),
    label: "parse_invoice",
  }
);
```

## Processing Many Files in a Loop

Call `extendTimeout()` each iteration — file operations poll the backend and can take a while.

```typescript
import { extendTimeout } from "@intuned/runtime";

for (const link of invoiceLinks) {
  extendTimeout();
  const data = await extractStructuredData(
    { type: "pdf", download: downloadFile({ page, trigger: link }) },
    { dataSchema: invoiceSchema, label: "parse_invoice" }
  );
  results.push(data);
}
```

## Available Exports

`toMarkdown`, `extractTables`, and `extractStructuredData` are the ONLY functions available from `@intuned/files` — do NOT import anything else. Exported types: `File`, `PdfFile`, `ImageFile`, `SpreadsheetFile`, `DocumentFile`, `ExtractedTable`, `FileOperationOptions`, `ExtractStructuredDataOptions`.
