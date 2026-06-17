---
name: create-intuned-project
description: "Create a new Intuned project for something the user wants automated on a website — scraping/data extraction, action automation, Crawlers, or RPA. Use when no Intuned project exists yet for what they're asking, including one-time needs. Explores the site with the user, plans, then builds and tests the APIs locally."
---

# Create Intuned Project

**Workflow:** URL, goal & language → explore & plan (enter plan mode) → get the plan approved → set up & provision the project → Use Subagents to build each API → test → finish up.

## Phase 1: URL, Goal, and Language

You need three things before you can plan:

- The **start URL** — where the automation will run.
- The **goal** — what the user wants done with the site.
- The **language** — Python or TypeScript.

A URL with no goal isn't enough, and a goal with no URL isn't either. If any of the three is missing, ask. If the user gave a URL but didn't say what they want done with it, don't infer — ask. Settle the **language up front**, so the plan and every API are written in the right one from the start. (If the user later says "crawler" with no language preference, Python is the better fit.)

Phrase your messages from the user's perspective. They don't know what an "Intuned project," "skill," or "API" is internally — talk about what you'll do for them, not the mechanics.

**Unsupported languages:** If the user explicitly asks for a language other than Python or TypeScript (e.g., Java, Go, Ruby, C#), tell them: "Intuned currently supports only **Python** and **TypeScript**. If you'd like support for other languages, please [contact our team](https://intunedhq.com/docs/main/06-resources/help-and-support)." Then ask which of the two they'd like.

Once you have all three, move on to exploring and planning. Explore the site directly — never ask the user to describe what's on the page.

**Browser binary:**
You will work on a chromium browser, you will control it via intuned CLI, you must always read `browser-management` skill to understand how to work with the browser.

## Phase 2: Exploration & Planning

Enter plan mode once you reach this phase, plan mode helps the user to read and review the plan.
Entering plan mode should be Before exploring, not after it.
**WRONG**:
navgiate -> discover, explore, ask user questions -> enter plan mode -> write plan -> exit plan mode

**CORRECT**:
navgiate -> enter plan mode -> discover, explore, ask user questions -> write plan -> exit plan mode

**Work in a planning mindset.** If your environment has a dedicated plan mode, enter it for this phase: explore and gather information without changing the site or writing project code until the plan is approved. Either way, the deliverable of this phase is a written plan the user signs off on — you present it and wait for them to **approve or ask for changes** before building anything.

**Hardcoded values**:
Never include hardcoded values in the API to be produced. Always ask the user for default values and if the user wants to parameterize them or not.

Examples:

**WRONG**:

- Scrape API request with 1000 items response.
- Loop over all pages without a max_pages parameter configured
- Filter Started Date on a hardcoded DD/MM/YY

**CORRECT**:

- Ask the user how many items does he want, should it be parameterized? should it have a default value?
- max_pages parameter to loop over 5 pages, ask the user for default pages.
- Filter on date passed from parameters. Ask the user for default date.

**Prefer x,y coordinates during exploration.** When you see an element in a screenshot, click it directly using coordinates - no need to find element IDs. This is faster and element IDs aren't needed until you build selectors.

`element_id` values are temporary IDs injected dynamically by the browser tools (they are **not** part of the real DOM); they only make the browser tools work and must never appear in the automation API code. The selectors that go into the project come from `build-selectors`, never an `element_id`.

### Two Types of APIs

**Data extraction APIs** extract or collect data from pages (scraping, monitoring, data mining). The **Data Extraction — Exploration & Planning Detail** section below has the specific exploration and planning guidance for these.

> For data extraction, aim to explore a list with **at least 2 items** so the sub-agent that builds the API can confirm selectors generalize rather than being hardcoded to a single row. If the page genuinely shows only one item and has filters/tabs that might surface more, ask the user before touching them — never change the site state without permission.

**Action automation APIs** perform actions on pages (form filling, bookings, approvals, multi-step workflows). Keep action APIs compact — split at natural boundaries in the workflow (e.g., searching vs booking are separate actions, but a multi-step form is one flow). During exploration, always complete the full workflow with dummy data to discover the success/failure state. Go through the entire flow so you know what verification looks like. Document exactly what changes after completion (URL redirect, modal, toast, status change) in the plan.

A project can have both types — e.g., a data extraction API that scrapes a list, chained to an action automation API that submits each item to a form.

### Handling Bot Detection

If you encounter any bot detection signal — **stop, do not reject, do not continue exploring**. Read the bot-detection skill immediately to handle it.

### Handling authentication

**If you discover restricted content** (login walls, gated downloads, "sign in to view", etc.) — handle it now, not after the plan. Ask the user if they have credentials, load the `auth-sessions` skill, create `.parameters/auth-sessions/create/<name>.json` (default name `default`) with the login fields as empty placeholders, and ask the user to fill in the values there — not in chat; you won't read them back. Then log in, verify it works, and continue exploring with an authenticated browser. You need to see the authenticated content to build a complete plan.

**Important:** Even if you are in plan mode and you are read-only, it is ok to create the auth-session file, since the user will write to it, not you. So you should create the file and you should not exit plan mode.

**If an API will need a secret or config value that isn't a login** — an API key, bearer token, account ID, base URL, etc. — note it in the plan and handle it with the `manage-env-vars` skill (have the user supply the value via the command or `.env` — never in chat — and read it from the environment in code). Never hard-code or invent these.

**Focus questions on what the user wants to achieve.** Implementation details like return values or schema fields are usually decisions you should make yourself. Ask about things that affect the user's workflow — like how they want to split the work, what data matters to them, or what counts as success.

### Questions Are Driven by What You See

**CRITICAL: Always investigate first, then ask.** Never ask a question without first seeing something on the site that prompts it.

```text
WRONG: "Do you want pagination?" → then look for it
RIGHT: See a "Load More" button → ask "I found a 'Load More' button with ~50 pages of results — should we handle pagination?" (load all pages / just the first / make it configurable)

WRONG: "What data do you want?" → without looking
RIGHT: Scroll through the page → ask "Each listing shows name, price, rating, and location. Which fields do you need?" (all of them [recommended] / just name and price / let me pick)
```

Every question should reference something specific you observed and offer clear options.

### Downloadable Files → Recommend Attachments

When you find downloadable files on a page — documents, PDFs, .docx/.xlsx/.csv, "Download"/"Export" links, attached forms — **recommend capturing them as Intuned attachments** (real downloaded files), not as plain links. Intuned has a first-class `attachment` type. `implement-api` has instructions on how to write the automation code to download the file, uploads it to storage, and returns an `Attachment` object the user can retrieve. That is almost always more useful than a bare URL (which may expire, require a session, or 404 later).

So when you ask the user about documents, make **downloading them as attachments the recommended option** — e.g. ask "Each detail page lists application documents (.docx/.xlsx). How should I capture them?" offering: download them as attachments (recommended) / just capture the file links / ignore the documents.

In the plan, give these fields the `attachment` type. The `handle-attachments` capability covers the full attachment model and how `implement-api` skill will download each file and returns it as an `Attachment`.

### Collect URLs for Selector Building

As you explore, collect URLs for each page type. The sub-agent that builds each API uses these to verify selectors generalize across different pages — so the more diverse examples you provide, the more robust the implementation will be.

- **Pages with unique URLs** (e.g., `/product/123`, `/product/456`): Click into multiple different entities and record each URL. Aim for 3+ but collect as many as you naturally visit during exploration.
- **Single-URL pages**: If all content is on one URL (list page, SPA, single form), that's fine — note it in the plan so `build-selectors` knows.

Use `intuned dev browser tabs list` to get URLs of open tabs. All collected URLs go in the plan under `### URLs Discovered`.

### Plan Rules

1. **Write the plan in the project's language** — once the language is confirmed, all language-specific content must reflect that single language. Do not mix Python and TypeScript references in the same plan.
2. **No implementation details** — No HTML, selectors, raw request payloads, or code. Those come later, when the sub-agents build the APIs.
3. **Include example URLs** — For every page type, include real URLs you discovered.
4. **Include the schema/return structure** — What the API outputs. The user reviews this in the plan.
5. **Include API access mode** — In `## Configuration`, include an explicit line: `API Access: Enabled` or `API Access: Disabled`. Enable it when the project needs standalone/on-demand Runs (including Run playground, app/SDK/API-key/external-client usage), RPA/action automation, computer-use / browser-use, crawling, or auth sessions. Disable it for normal jobs-only scrapers. You apply this to `Intuned.json` during Phase 3 project setup.

> **Bot-detection note:** If exploration surfaces a CAPTCHA or other bot-detection You must immediately invoked `bot-detection` skill. You can and should configure stealth mode and the CAPTCHA solver (in `Intuned.json`, plus the solver's code helpers) so they're in place and take effect once the project runs on the platform — they simply don't engage during local dev, so there's nothing to "test" locally. A normal user-supplied proxy (see the `proxy` skill) is the one such lever that also works locally.

> Do not use askUserQuestion to ask the user for the proxy, ask it immediately as a free text.

## Data Extraction — Exploration & Planning Detail

Specific exploration and planning guidance for **data-extraction** projects (scraping, data mining, monitoring) — the question patterns, how to decide the API structure and chaining, and the plan and schema shapes you'll present for approval. If you're building only action-automation APIs, you can skip this section.

## What to Discover

1. **User's goal** — What does the site contain? What is the user likely after?
2. **Data location** — Where is that data? What fields are available?
3. **Page hierarchy** — list → detail, category → subcategory → item, search → results, etc.
4. **Pagination** — Is there pagination? What type (numbered pages, "Load More", infinite scroll)? **How do you know when it's exhausted?** If you find pagination, ask the user if they want to handle it. If yes, note the pagination type and exhaustion condition.
5. **Filtering options** — Are there filters (dropdowns, checkboxes, search bars)? If you find filtering, ask the user if they're interested in filtering the data. If yes, explore the available filter options and ask which specific filters they want to support.
6. **How the data is exposed** — does the data live in the rendered HTML, or does the page fetch it from a backend endpoint (XHR / fetch / GraphQL) you could call directly? Look at the network captures while the page loads or you interact. This decides whether the API extracts via **DOM selectors**, a **network request**, or both — see the next section.

## How the Data Is Exposed: DOM vs Network

For every API, decide how it will get its data. The two approaches are equally valid, Prefer Network approach over DOM, network can be faster and more reliable.

Start with checking network requests.

- **Network request** (`find-network-requests` capability) — call the backend endpoint the page itself uses and read structured JSON. **Best when** the page loads data from an XHR/fetch/GraphQL endpoint (especially infinite-scroll or filtered lists), you want all fields at once, or the DOM is messy/virtualized. **Cons:** the endpoint may need auth/tokens/headers captured from the page first, and its response shape can change.

- **DOM selectors**: read values out of the rendered page. **Best when** the data is in the HTML, the page renders without a clean backing API, or the markup is stable. **Cons:** breaks if the layout changes; needs pagination/scroll handling to load everything.

**How to decide:** while exploring, watch the network captures (`intuned-agent/tab_${tabId}/network/`). If a single backend call returns the data you need, prefer the network request — it's usually more robust and complete than scraping. If the data only exists in the DOM, or the endpoint is heavily protected, use selectors. When a flow mixes both (e.g. a list endpoint but detail only in HTML), use each where it fits. **Record the choice in the plan** for each API.

---

## Drill-Down: Pagination & Filtering

When you discover pagination or filtering, don't just note it — **investigate further and ask the user**.

**Pagination:** If you see pagination controls, ask — e.g. "I found pagination ('Next' button / page numbers / infinite scroll). Scrape all pages or just the first?" offering: all pages / just the first page / make it configurable (max pages parameter) [recommended].

**Filtering:** If you see filter options, ask first whether the user is interested, then drill down:

- First: "I found filtering options (e.g., Category, Price Range, Location). Want the scraper to support filtering?" → yes, let me pick which filters / no, scrape everything unfiltered [recommended].
- If yes, explore the specific options and ask which ones: "Here are the available filters: Category (15 options), Price Range (5 brackets), Location (city dropdown). Which should the API support?" → all of them / category and price range / category only [recommended] / let me specify.

This pattern applies to any interactive feature you discover — always ask if the user cares about it before diving deeper.

---

## Decide API Structure

**You decide the most logical API structure based on what you discovered.** Don't ask the user how many APIs to create — include your recommended structure in the plan and the user can approve or request changes.

**Default: prefer splitting into multiple APIs.** Separate APIs are easier to debug, test, reuse, and run in parallel.

Only ask about API structure when there's a genuinely ambiguous tradeoff that the user should weigh in on.

### Common Patterns

Pick the pattern that fits the site. These are examples, not an exhaustive list — use your judgment.

| Site Pattern        | Recommended API Structure                                       | Example                                                           |
| ------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------- |
| List + detail pages | **2 APIs**: list (extracts links) → detail (extracts full data) | Job board: `list_jobs` → `get_job_details`                        |
| Category hierarchy  | **2-3 APIs**: categories → subcategories → items                | Directory: `list_categories` → `list_businesses` → `get_business` |
| Single data page    | **1 API**: extract everything from one page                     | Dashboard: `get_metrics`                                          |
| Paginated list only | **1 API**: list with pagination, no detail pages                | News feed: `get_articles`                                         |

**When you include API structure in the plan, briefly explain why you chose that split.** This helps the user understand and suggest changes if needed.

### How APIs Chain Together: `extend_payload`

When you split into multiple APIs, the first API passes data to the next using `extend_payload()` (Python) or `extendPayload()` (TypeScript). This schedules a run of the next API with the payload you provide.

**The key question when splitting APIs is: how does the second API reach a specific entity?** You must figure this out during exploration before committing to a split.

#### Step 1: Check if Direct URL Linking Works

**You MUST click into at least 2 different entities during exploration and compare the URLs you land on.** This is not optional — do not decide on URL linking without doing this.

Procedure:

1. From the list page, click on entity #1 → note the full URL
2. Go back to the list page, click on entity #2 → note the full URL
3. Compare the two URLs. Look for a part that changed (an ID, slug, name, query param)

**URL linking works when each entity has a distinct URL:**

- Entity 1: `/product/123`, Entity 2: `/product/456` → ID changes, URL linking works
- Entity 1: `/jobs/engineer-at-google`, Entity 2: `/jobs/scientist-at-meta` → slug changes, URL linking works
- Entity 1: `/listing?id=abc`, Entity 2: `/listing?id=def` → query param changes, URL linking works

**URL linking does NOT work when URLs are identical:**

- Entity 1: `/external/biddetails`, Entity 2: `/external/biddetails` → same URL, URL linking will NOT work
- Entity 1: `/dashboard`, Entity 2: `/dashboard` → same URL, this is an SPA
- Content loads in modals/panels without any URL change

**If you only visited one detail page, you have NOT verified URL linking.** A single URL like `/item/details` looks like it could be unique, but you won't know until you visit a second one and compare. Never claim "URL linking works" based on one example.

If URLs are unique → use **URL-based chaining**. The first API extracts URLs (hrefs), and the second API navigates directly to them.

#### Step 2: If URLs Are Not Unique (SPAs)

When all entities share the same URL, **we still prefer splitting into two APIs** — large item sets make single-API approaches fragile (one failure in one item can break the entire run). The challenge is finding how the second API locates a specific item.

**Process: Identify unique fields, then find the item by those fields.**

**2a. Identify unique fields for the entity**

Look at the list data and find what makes each entity unique. This could be:

- A unique ID (e.g., bid number, product SKU, order ID)
- A title or name
- A combination of fields (e.g., ID + title together)

The first API extracts these unique fields and passes them via `extend_payload`.

**2b. Determine how the second API finds the item using those fields**

Try these approaches in order of preference:

1. **Use the site's own search/filter** — If the site has a search bar or filter functionality, the second API can search for the entity by its unique field (e.g., search by bid number or title). This is the most reliable approach because it works regardless of pagination.

2. **Filter rows by text** — If there's no search but the list is visible, the second API can scan the rows for matching text (the unique ID or title). **If the list has pagination, the second API must paginate through pages until it finds the item** — loop through pages and check each one, break when the item is found.

3. **Extract the onclick/navigation script** — If no unique text param works, inspect the elements that open the detail view. They often have `onclick` handlers or JavaScript calls (e.g., `openDetails('abc123')`, `window.location='...'`). The first API extracts this script, and the second API executes it to open the details.

4. **Get data from network requests** — Check the page's network requests for data endpoints. The second API may call these directly with an ID found in the page data; the system keeps tracking of the network requests within `intuned-agent/tab_${tabId}/network/` directory, you can use it to find the correct network request.

5. **Avoid fragile approaches**: Avoid giving fragile parameters that may not last on long terms, for example if you give item's index number in a list, then it can change over time when a new item is added or removed from the data list, this item's index will become invalid.

**Tip (plan handoff for network APIs):** If list or detail data depends on programmatic requests, briefly describe what you observed in the plan — method, URL pattern, and any prerequisite (e.g. a token captured from a prior request). The `find-network-requests` skill will navigate to the page and identify the request from the network captures. See **`auth-sessions`** → _Authenticated backend calls_ for auth-specific notes.

You are not limited to these approaches, you can use any approach that you see works, the main goal is to find the most reliable approach to link the two APIs together.

In these cases, the "list + detail" pattern becomes a single API that iterates through items, clicking into each one and extracting data before going back.

#### Chaining Payload: What to Pass

Once you've decided how to link, the `extend_payload` should include:

1. **The linking field** — whatever the second API needs to reach the entity (URL, ID, selector, script etc.)
2. **ALL other extracted fields** — pass every field the first API extracted, not just the linking field. This ensures the final output has the complete dataset.

For example, if `list_jobs` extracts `title`, `company`, `location`, and `detail_url`, the `extend_payload` should include all four — not just `detail_url`. The `get_job_details` API then merges its own extracted fields with the forwarded ones.

#### In the Plan, Always Specify

1. **How you determined the linking strategy** — "URLs are unique (checked 3 examples: /item/1, /item/2, /item/3)" or "SPA — all items open at /app, using internal API endpoint instead"
2. Which API chains to which
3. What fields are passed in `extend_payload` (all extracted fields + the linking field)
4. How the next API uses the linking field (navigate to URL, click selector, call endpoint, etc.)

---

## Build the Plan

**Describe pagination exhaustion** — if pagination exists, describe how to know when it's done.

**Pagination example:**

```
- **Pagination**: Click-based. Exhausted when "Next" button is no longer visible.
```

**NOT this:**

```
- **Pagination**: `<a class="pagination-next">Next</a>`  <- NO selectors in plan
```

### Plan Template

```markdown
## Plan: {goal}

### Configuration

- **Start URL**: {url}
- **Auth Required**: {Yes/No — if yes, note that credentials were tested and the login URL}
- **Project Type**: Data Extraction

### URLs Discovered

Include all URLs you visited during exploration. The sub-agent that builds each API uses these to verify selectors generalize.

- **Login page**: {login URL, if auth required}
- **List page**: {actual URL from exploration}
- **Detail pages**: {list all detail URLs you visited}
  - {detail_url_1}
  - {detail_url_2}
  - ...

### Auth Session APIs (if auth required)

#### auth-sessions/create

- **Login URL**: {login page URL}
- **Credential fields**: {what the form needs — e.g., email + password}
- **Success indicator**: {what element confirms login succeeded — e.g., "user menu appears"}

#### auth-sessions/check

- **Protected page**: {URL to check}
- **Logged-in indicator**: {what element proves the session is valid}

### APIs

#### 1. {api-name} (Entry Point)

- **Description**: {what it extracts}
- **Parameters**: {user inputs}
- **Navigation**: {human-readable steps, no selectors}
- **Extraction**: {DOM selectors / network request / both — and for a network request, the method + URL pattern you observed and any prerequisite like an auth token from a prior request}
- **Schema**: {fields to extract}
- **Pagination**: {type and exhaustion condition}
- **Chains to**: {next API or none}

### Relationships

- {how APIs connect}
```

---

## Schema in the Plan

Each API needs its own schema. **Include the schema directly in your plan** - the user will review and approve/reject the entire plan including schemas.

**Do NOT ask for schema confirmation separately.** The schema is part of the plan. When you present the plan for approval, the user sees the full plan including schemas and can approve or ask for changes.

If you have multiple APIs (e.g., `list-products` and `get-product-details`), include separate schemas for each in the plan.

### Supported Field Types

| Type         | Use For                           | Example Value           |
| ------------ | --------------------------------- | ----------------------- |
| `string`     | Text content                      | "Product Name"          |
| `number`     | Numeric values                    | 29.99                   |
| `boolean`    | True/false                        | true                    |
| `url`        | Links, images                     | "/products/123"         |
| `date`       | Date/time values                  | "2024-01-15"            |
| `array`      | Lists (specify item type)         | ["tag1", "tag2"]        |
| `object`     | Nested data structures            | {name: "...", value: 1} |
| `attachment` | Downloadable files (PDFs, images) | "document.pdf"          |

### Schema Field Structure

Each field in the schema should have:

- **name** (required): Field name
- **type** (required): One of the types above
- **example** (recommended): Sample value to show the user
- **description** (optional): What this field represents

### Example Schema Presentation

```markdown
Here's the proposed schema for **list-products**:

| Field       | Type    | Example         | Description                                 |
| ----------- | ------- | --------------- | ------------------------------------------- |
| title       | string  | "Product Name"  | Product title                               |
| price       | number  | 29.99           | Price in dollars                            |
| details_url | url     | "/products/123" | Link to detail page (required for chaining) |
| in_stock    | boolean | true            | Availability status                         |
| tags        | array   | ["sale", "new"] | Product tags (array of strings)             |
```

### Locked Fields for API Chaining

When a field is required for chaining (like `details_url` for list -> detail), clearly note this in the description so the user understands it shouldn't be removed.

---

## Data Extraction: Phase 2 Checklist

- [ ] Site fully explored — pagination, filtering, page hierarchy understood
- [ ] User's goal confirmed (via MCQ questions)
- [ ] URLs collected for each page type (multiple for detail pages when possible)
- [ ] API structure decided (your best judgment, splitting preferred)
- [ ] Schema included in plan for each API
- [ ] Relationships between APIs clear
- [ ] If auth required:
  - [ ] Credential parameter file written with placeholder fields for the user to fill in directly (values never entered in chat)
  - [ ] Login verified (credentials actually work)
  - [ ] Authenticated content explored
  - [ ] Auth session APIs included in plan (create + check)
- [ ] Plan ready to present for user approval

---

## Set Up the Project Files (during planning)

Initialize the project files **before you present the plan for approval** — that lets you confirm the language and show the user the file tree as part of the plan. This is local file setup only; **don't provision or deploy here** — you provision in Phase 3 (after the plan is approved), and deploy is suggested at the end.

**Load the `initialize-project` skill** and follow it to choose the template that fits the goal, run `intuned dev init`, and install dependencies. `intuned dev init` creates `Intuned.json` from the template — you'll set its real metadata in Phase 3. Show the user the file-tree summary before moving on.

## Present the Plan for Approval

Present the finished plan and wait for the user to **approve it or ask for changes**. If your environment has a plan-approval step, use it; otherwise post the plan in chat and ask the user to reply "approve" or tell you what to change. Don't start building until they've approved.

## Phase 3: Project Setup

Once the plan is approved, set up the project yourself directly. You stub the API files here; the Phase 4 sub-agents fill them in. Do this:

1. **Clean up template leftovers** — delete template files that don't belong to this project:
   - `api/` — remove the template example API files (e.g. `sample.py`); you create your own stubs in step 2.
   - `auth-sessions/` — if the plan has **no** auth, delete the directory; if it does, you'll fill it in Phase 4.
   - `auth-sessions-instances/` — always delete if present (stale browser state).
   - `intuned-resources/jobs/*.job.json` and `intuned-resources/auth-sessions/*.auth-session.json` — delete all template files; you write the real ones in Phase 5.
   - Never touch auto-generated files: `pyproject.toml` (Python); `package.json`, `tsconfig.json` (TypeScript).
   - Never read anything under `.parameters/auth-sessions/create/` (credentials).
2. **Stub the API files**: write one file per planned API at `api/<api-name>.{py|ts}` (hyphenated names, matching the plan) so the Phase 4 sub-agents have functions to fill in. Use the file shapes from the `implement-api` skill (and its `api-patterns.md`), but leave them as **mocks**:
   - the imports the API needs, and a `DATA_SCHEMA` with **empty** `properties` (`array` for list APIs, `object` for detail/simple);
   - a **navigate** function, an **action/extract** function, and **pagination** functions if the plan calls for them; name them from the plan and leave each body as a `# TODO:` / `// TODO:` describing the plan's steps and returning an empty result;
   - the **`automation`** (Python) or **`handler`** (TypeScript) entry point wiring navigate, then action, then `validate_data_using_schema`, plus an `extend_payload` block only for APIs that chain;
   - `auth-sessions/create` and `check` stubs only if the plan has auth.
   - Important: Do not write any selectors or logic here (that is Phase 4). Do not fill in locators, queries, inputs or anything, this is subagents' work.
   - The language's type/build check may fail since these are Stubs, ignore these and leave the fix for the subagents. Your job is to write the stub, placeholders and TODOs, not fill in the the code and writing implementations.

3. **Set `Intuned.json` metadata** — read `Intuned.json` and set:
   - `apiAccess.enabled` from the plan's `API Access: Enabled/Disabled` line.
   - `metadata.defaultRunPlaygroundInput` = `{ "apiName": "<entry-point API>", "parameters": <default params> }` (the entry-point API's filename without extension; first one if several).
   - Leave everything else unchanged.
4. **`.gitignore`** — ensure it ignores `.intuned/`, `.intuned-agent/`, `traces/`, `.env`, `.venv/`, `node_modules/`, `__pycache__/`. Append any missing lines; don't reorder existing ones.
5. **Install dependencies** if not already: `uv sync` (Python) or `yarn install` (TypeScript).
6. **Provision the project** — register the platform-side project now. This does **not** deploy or run anything; it just creates the project so platform-scoped features (project env vars, and **attachment / managed-S3 uploads**, and End-To-End testing) work while you build, and so deploying at the end is a single step. Provisioning is what lets the runtime upload attachments — without it, attachment uploads fail with a `401`.
   1. **Pick a name for the project**: Pick a descriptive name for the project you are creating and provision it, proceed with this without confirming with the user.
      **Name rules:** 1–200 chars; letters, numbers, hyphens, underscores only; must start and end with a letter or number; hyphens/underscores only between alphanumeric segments.

   2. **Add `"projectName": "<name>"` to the settings file** (`Intuned.json` / `Intuned.jsonc`) before provisioning.

   3. **Provision** (it reads the name from the settings file):

      ```bash
      intuned dev provision --non-interactive
      ```

   4. **Confirm it worked** — run `intuned platform project get --json`; it should return the project. **Provision exactly once** — don't re-provision under another name. On a **409 / "already exists"** conflict, the name is taken (often by an existing IDE project) — ask the user for a different name rather than silently appending suffixes.

You write the README in the final step. Proceed to Phase 4.

## Phase 4: Build Each API

Build every API by **offloading to a sub-agent**: it works out the API's data source (selectors and/or the backend network request) and implements the code. Don't write selectors, network calls, or API code in your own context.

### How to spawn a sub-agent

Launch **one sub-agent per API**. That single sub-agent works out the API's data source (DOM selectors and/or the backend network request) **and** writes and tests the implementation, all in one pass. In its prompt:

This applies to both DOM and Network approaches, Including all Crawlers, RPAs, Authentications, Bot detection and any type of API. The subagent agent has instructions on what to do for any type of API. You are not allowed to write any API Implementation by yourself, you must always deligate to subagents.

- Tell it which capabilities to **load first**: `build-selectors` and/or `find-network-requests` (per the plan's extraction method) for working out the data source, then `implement-api` (plus `intuned-browser` for helper signatures) for writing the code.
- Give it the context it needs (it doesn't share your conversation): the **API name**, the **API file path** (`api/<api>.{py|ts}`), the **full plan section for that API verbatim** (extraction method, navigation, schema, pagination — don't summarize), the **URL(s)** to work against, and the **browser tab id** to use.
- **Very important:** it works only on its assigned tab — it must not use or close other tabs.
- It should read `api-patterns` to understand how to write patterns correctly.
- Tell it to do the whole job end to end, in this order:
  1. **Work out the data source** — use `build-selectors` (`build_reliable_selector` / `build_field_selector`) for DOM selectors and/or `find-network-requests` for the backend request, following the plan's extraction method.
  2. **Write the API implementation** — follow `implement-api` to fill in the navigate / action / pagination functions and the entry point, mapping each schema field to its selector or response field. Mark a schema field required only if it appears on every page tested.
  3. **Write the API's default input file** at `.parameters/api/<api>/default.json` — a representative input; for a chained/detail API, an example of the forwarded payload.
  4. **Test it locally** with `intuned dev attempt api` and fix until it passes. Use small values for parameters, don't run the API across many pages.
- If auth is enabled, the sub-agent does **not** log in or handle auth itself — the browser is already authenticated from the auth step. It builds selectors on the protected pages as normal, and adds `--auth-session <id>` to its test command (`intuned dev attempt api <name> <params> --auth-session <id> --cdp-browser-name default`), which injects the saved session. Pass it the **auth session ID** from the auth step.
- Ask it to **report back**: the functions it implemented, and the local test result (pass/fail with the parameters it used).

### Parallelism and browser tabs

Independent APIs can be built **in parallel** — one sub-agent each (for example, 2 sub-agents building 2 different APIs at once). **Each parallel sub-agent needs its own browser tab** so they don't collide: create one per API with `intuned dev browser tabs create` and pass that tab id in the sub-agent's prompt. A list→detail chain is two APIs that can run in parallel (you collected detail URLs during exploration).

### Auth-First Sequencing (if auth is enabled)

When the plan includes auth session APIs (`auth-sessions/create` and `auth-sessions/check`), build them **before** all other APIs and **not in parallel with them** — auth work changes the browser's login state, so it must be serialized. Once `auth-sessions/create` is implemented and run, every other API can use the resulting auth session.

The two auth APIs are coupled — run a **single localization** for both (`create` + `check` together), then a **single codegen** for both. Don't run separate passes per auth API.

#### Why the browser must start logged out

The auth sub-agent needs a **logged-out browser** to build its selectors. After Phase 2 exploration the browser is authenticated, and you can't see the login form (so you can't build selectors for it) while logged in. So restart the browser once — before spawning the sub-agent — to drop it back to a clean, logged-out state.

That is the **only** restart needed. The sub-agent builds the login selectors while logged out, logs in to build the success/check selectors, then implements and runs `create` and `check`. When it finishes, the browser is authenticated and the auth session is saved — exactly the state the other sub-agents need — so there is nothing to restart afterward and no mid-task restart.

Full sequence (auth is serialized — no parallel sub-agents during these steps):

1. **Restart the browser** (you) to a logged-out state → spawn **one auth sub-agent** (`create` + `check` together) that builds the selectors and implements and runs both APIs.
2. **All other APIs** — build them via sub-agents (the browser now has a valid auth session); these may run in parallel.

**Step 1 — Restart the browser to a logged-out state before spawning the auth sub-agent:**

```bash
# The browser is authenticated from Phase 2 exploration.
# Restart to a clean, logged-out state — the sub-agent must see the login form to build its selectors.
intuned dev browser stop
intuned dev browser start --headless
intuned dev browser tabs create   # → returns the id for the new tab
```

**Step 2 — Spawn one auth sub-agent** (covering both `auth-sessions/create` and `auth-sessions/check`):

In its prompt (tell it to load `build-selectors`, `implement-api`, and the `auth-sessions` skill first):

- The browser is in a fresh, logged-out state at the login page. Give it the **login URL**, the `auth-sessions/create` + `auth-sessions/check` sections from the plan (verbatim), and the **browser tab id**.
- Use the `auth-sessions` skill's `list-credentials.sh` to get the stored credential field names (it lists them without exposing values). Always fill credentials via the auth-param mechanism — never literal values.
- It must do the full job in one pass, **without restarting the browser**:
  1. **Build selectors** with `build-selectors` for all login form fields, the success indicator (`create`), and the logged-in check element (`check`). Build the login-form selectors while logged out, then log in to build the success/check selectors — it must see both states.
  2. **Implement** `auth-sessions/create.{py|ts}` and `auth-sessions/check.{py|ts}` following `implement-api`.
  3. **Run and verify** both with the `intuned` commands from the `auth-sessions` skill (those commands handle the login lifecycle themselves). Report the resulting **auth session ID** — other APIs will reference it.

### For Each Remaining API

Build each remaining API with its own sub-agent, following "How to spawn a sub-agent" above. Run independent APIs in parallel, each with its own browser tab; a list→detail chain is two APIs you can build in parallel (you collected detail URLs during exploration). Per API, make sure the sub-agent gets:

- **All the URLs you discovered** for that page type — for selectors, multiple pages let `build-selectors` produce selectors that generalize (for a `details` API, several entity URLs; for an entry-point `list` API, the start URL alone is fine); for a network-based API, the URL(s) where you observed the backend request.
- The **entire API section from the plan** verbatim — including the **extraction method** (selectors / network request / both) — never summarized.
- The **browser tab id**, and (if auth is enabled) the **auth session ID** from the auth step — it tests with `--auth-session <id>` and never handles login itself (the browser is already authenticated).

## Phase 5: Create Auth Sessions & Jobs

This phase has two sections:

1. **Auth Sessions** — only run this section if the project has auth sessions enabled
2. **Jobs** — always run this section

### Cleanup: Remove Leftover Resource Files

Before creating any new resource files, remove stale files that were copied from the project template but are not relevant to this project's APIs.

**For jobs** — if `intuned-resources/jobs/` already exists, list all `*.job.json` files inside it. Delete every file whose `apiName` does not match any API file in `api/`. These are template leftovers and must be removed before writing the new job files.

**For auth sessions** — if `intuned-resources/auth-sessions/` already exists, delete **all** `*.auth-session.json` files currently in it. These files were generated by `intuendctl dev init` as template placeholders and were not created by you. You will write the correct auth-session files in Section 1 below.

---

### Section 1: Auth Sessions (only if auth sessions are enabled)

If the project has auth sessions enabled (i.e. `Intuned.json` has `"authSessions": { "enabled": true }`), create the auth-session resource files first — before any job files — because the job files will reference the auth-session IDs.

Create `intuned-resources/auth-sessions/` at the project root. Each credential parameter file in `.parameters/auth-sessions/create/` becomes one auth-session file:

```
intuned-resources/auth-sessions/<name>.auth-session.json
```

The file format is:

```json
{
  "parameters": {
    // <parameters copied from .parameters/auth-sessions/create/<name>.json>
  }
}
```

**Because the parameter files contain sensitive credentials, do NOT read or echo them directly.** The `auth-sessions` skill provides a `create-auth-sessions.sh` script for exactly this — load that skill and run its `scripts/create-auth-sessions.sh` from the project root. It reads the stored credential files (without exposing their values in logs) and writes one `.auth-session.json` per credential set (e.g. `default.auth-session.json`).

The file names produced by this script **must match the `--id` values used when implementing auth in Phase 4**. They will — both derive from the same credential file name (e.g. `default.json` → `--id default` when running `auth-sessions/create` → `default.auth-session.json` here). This consistency is what lets the platform resolve the auth session at runtime. You can obtain it by reading `auth-session-instances/<name>`, the name is the one created when the auth session was run.

After the script finishes, note down the names of all created auth-session files (the `<name>` part without `.auth-session.json`) — you will need them in Section 2.

---

### Section 2: Jobs

Create a `intuned-resources/jobs/` directory at the project root (sibling to `api/`). If `intuned-resources/jobs/` already exists, write the job files into it.

For the full job schema and field reference, load the `manage-jobs` skill.

### Which APIs get jobs

The purpose of jobs is to test all created APIs and achieve full coverage. A single job for an API that uses `extend_payload` will achieve coverage for 2 APIs: the main API and the API called in the `extend_payload`, since it will run with it. A standalone API is not covered by any other job, so it needs its own job.

Before creating job files, review all APIs in the project and classify them:

- **Needs a job:** The API is a standalone API, or it calls other APIs via `extend_payload`.
- **Skip:** The API is called by another API via `extend_payload`. It already runs as part of its caller's job.

### File Naming

`{name}.job.json` — short (1–3 words), kebab-case, derived from the API name and what it collects.

Examples: `scrape-listings.job.json`, `collect-products.job.json`, `get-prices.job.json`

#### Rules

- `apiName` must exactly match the API filename in `api/` (without the extension)
- `parameters` must match the keys found in `.parameters/api/{api-name}/`
- **NEVER add a `schedule` field unless the user explicitly provided schedule details.** Omit it entirely by default — do not invent or assume any schedule.
- **If auth sessions are enabled, every job file MUST include an `auth_session` field.** Use the auth-session name (the `<name>` from the `.auth-session.json` filename) as the `id`. A job without `auth_session` will fail on any page that requires authentication.

#### Example — no auth sessions

A project with three APIs: `search-listings.py`, `listing-detail.py`, `get-prices.py`. `search-listings` calls `listing-detail` via `extend_payload`. `get-prices` is standalone.

- `search-listings` → **needs a job** (calls other APIs via `extend_payload`)
- `listing-detail` → **skip** (called by `search-listings` via `extend_payload`)
- `get-prices` → **needs a job** (standalone API)

Result: two job files — `scrape-listings.job.json` and `get-prices.job.json`.

**`intuned-resources/jobs/scrape-listings.job.json`**:

```json
{
  "payload": [
    {
      "apiName": "search-listings",
      "parameters": {
        "search_query": "software engineer",
        "location": "San Francisco, CA",
        "max_pages": 5
      }
    }
  ],
  "configuration": {
    "maxConcurrentRequests": 2,
    "retry": { "maximumAttempts": 3 }
  }
}
```

#### Example — with auth sessions

Same project, but auth sessions are enabled. Section 1 created `intuned-resources/auth-sessions/default.auth-session.json`, so the auth-session ID is `default`. Every job must include `auth_session`:

**`intuned-resources/jobs/scrape-listings.job.json`**:

```json
{
  "payload": [
    {
      "apiName": "search-listings",
      "parameters": {
        "search_query": "software engineer",
        "location": "San Francisco, CA",
        "max_pages": 5
      }
    }
  ],
  "configuration": {
    "maxConcurrentRequests": 2,
    "retry": { "maximumAttempts": 3 }
  },
  "auth_session": {
    "id": "default",
    "checkAttempts": 3,
    "createAttempts": 3
  }
}
```

> **Note:** `schedule` is omitted — only add it if the user explicitly specifies when the job should run. The `manage-jobs` skill explains how to add a schedule when needed.

---

## Phase 6: Testing

Two layers of testing. The **local API tests are already done by the API sub-agents in Phase 4**, so here you **review their results** rather than re-running anything. The **end-to-end platform test** you present to the user and run only if they want it, since it runs on Intuned's infrastructure, so it's their call.

### Local API tests

Each API was **already tested locally by its sub-agent in Phase 4**: the sub-agent ran `intuned dev attempt api <name> <param>...`, reported pass/fail, and the full result was saved under `.intuned-agent/platform-attempts/...`. Take the sub-agents' results instead: read the saved result files and confirm the whole set holds together (the automation works, every expected field is populated, no execution errors).

Local testing is **limited**: it covers one API at a time and does NOT exercise `extend_payload` / API chaining (that only runs as a job, see the e2e test below).

### Show the user results, then ask about the platform test

A. Before the platform test, prove the APIs work. The API sub-agent will already have run the code (because you asked it to) and written the results to `.intuned-agent/platform-attempts/*`. You should make sure there are no duplicate data (infinite extracting loops), no corrupted data (e.g: all nulls) and return to the user one friendly, well-structured message.

b. Write a message to the user: Keep it user-facing: no selectors, internal paths, or process detail, gives a feeling of success. It will show a summary of what was implemented (do not mentioned selectors and implementation details), how many data extracted, where to view them.
Example of a message:

````markdown
The API x is built and all sites pass. Here's a summary:

api/name.py: <What it does..>
Parameters:
┌───────────────┬───────────────────────────────────────────────┐
│ Param │ Description │
├───────────────┼───────────────────────────────────────────────┤
│ x │ y │
├───────────────┼───────────────────────────────────────────────┤
| ... ..
└───────────────┴───────────────────────────────────────────────┘

Per page outpage: <Output here>

Test results:
<Json or markdwon or any sort of proper format for the results>

Key implementation notes:
<notes>

To run locally:

```bash
intuned dev attempt api <name> <parameters_path>
```
````

<NEVER MENTION>

````

c. Then **ask whether they want an end-to-end test job**, explaining in plain terms what it is and that it might take longer time to execute, for example:

> An end-to-end test job runs on the Intuned platform. It uses Intuned's infrastructure to spin up browsers and run the API across the whole site for the job input you give it, so on a large site it covers everything, not just the sample you saw locally. It can take a while depending on the API and the inputs.

Run the test job below only if they say yes. Either way, finish with the README and wrap-up steps that follow.

### End-to-end test job

Local tests pass one API at a time — they don't prove the project works as a whole or that the `extend_payload` chain runs. A **test job** does: it runs the project's code from the current directory on the platform's execution environment end-to-end, chaining included, and validates the deploy environment directly — without a real deploy. Run it only if the user agreed to it above.

Load the **`test-intuned-project`** skill — it's the source of truth for triggering and monitoring test jobs. In short:

1. **Create `intuned-resources/jobs/e2e.job.json`** with a `payload` entry for **every entry-point API** (entry-point = not reached via `extend_payload` from another API). Set `configuration.retry.maximumAttempts` to `2`.
2. **Trigger one test job from it** — one run covers the whole project and the full chain:

   ```bash
   intuned dev test-job trigger --from-job-config intuned-resources/jobs/e2e.job.json --max-runs <n> --json
````

Pick `--max-runs <n>` per the `test-intuned-project` skill.

3. **Monitor it to completion and diagnose any failures** per that skill, fixing the code until the run is clean.

Once testing is done (local tests pass, plus the e2e job clean if the user ran one), write the project `README.md` (language-specific: target site, each API with its schema, how to run locally).

## Finishing

The project is done when every API passes local tests (and the end-to-end test job runs clean, if the user ran one). Wrap up with a concise plain-text chat summary — no jargon, no selectors, no phase/process detail:

- **Lead with the result** — "Done. Here's what's ready:" then list each API and what it does.
- **Flag anything that didn't work** — briefly, what and why, including any limitation you hit.
- **How to run** — how the user runs it locally (`intuned dev attempt api ...` / running a job). Keep it short.
- **Suggest going live** — the project is built, tested, and already provisioned (it runs locally for now). When they're ready, you can put it live on the Intuned platform (scheduled Jobs, on-demand Runs) by **deploying**. Offer it; don't do it unprompted.

To go live (only once the user agrees):

```bash
intuned dev deploy --non-interactive
```

## Consulting the docs

For more info, search the Intuned docs using the `search_intuned` and `query_docs_filesystem_intuned` tools.
